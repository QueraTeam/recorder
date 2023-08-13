var Xvfb = require('xvfb');
var puppeteer = require('puppeteer');
const { spawn, spawnSync } = require('child_process');

async function record(fileName, url, username, password) {
    var xvfb = new Xvfb({
        reuse: false,
        xvfb_args: [
            "-screen", "0", "1920x1080x24",
            "-ac",
            "-nolisten", "tcp",
            "-dpi", "96",
            "+extension", "RANDR"
        ]
    });
    xvfb.startSync();

    var browser = await puppeteer.launch({
        headless: false,
        executablePath: '/usr/bin/google-chrome',
        defaultViewport: {width: 1920, height: 1080},
        ignoreDefaultArgs: [
            "--mute-audio",
            "--enable-automation"
        ],
        args: [
            "--no-sandbox",
            "--use-fake-ui-for-media-stream",
            "--window-size=1920,1080",
            "--start-fullscreen",
            "--disable-notifications",
        ],
        userDataDir: "./profile",
    });
    const page = await browser.newPage();
    await page.goto(url);
    await page.locator("input#username").fill(username);
    await page.locator("input#password").fill(password);
    await page.click(".login-btn");
    const listenerButton = await page.waitForSelector("div >>> ::-p-text(ورود به عنوان شنونده)");
    await listenerButton.click();

    var options = [
        "-video_size", "1920x1080",
        "-framerate", "30",
        "-f", "x11grab",
        "-draw_mouse", "0",
        "-i", xvfb._display,
        "-f", "pulse",
        "-ac", "2",
        "-i", "default",
        "-vf", "format=yuv420p",
        `/output/video/${fileName}.mkv`
    ];

    var cmd = 'ffmpeg';
    var proc = spawn(cmd, options);

    proc.stdout.on('data', function (data) {
        console.log(data);
    });

    proc.stderr.setEncoding("utf8")
    proc.stderr.on('data', function (data) {
        console.log(data);
    });

    proc.on('close', async function () {
        console.log('finished');
        xvfb.stopSync();
    });
}

const args = process.argv.slice(2);
const [fileName, username, password, url] = args;
record(fileName, url, username, password);
