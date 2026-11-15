// Render window.renderFrame(t) frame by frame and pipe PNGs into ffmpeg -> H.264 MP4.
//   node capture.mjs index.html out.mp4 [fps]
import { chromium } from 'playwright';
import { spawn } from 'node:child_process';
import { resolve } from 'node:path';
import { pathToFileURL } from 'node:url';

const [html, out, fpsArg] = process.argv.slice(2);
const fps = Number(fpsArg || 30), W = 1080, H = 1920;

const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: W, height: H }, deviceScaleFactor: 1 });
page.on('pageerror', e => console.error('PAGE ERROR:', e.message));
await page.goto(pathToFileURL(resolve(html)).href);
await page.evaluate(() => document.fonts.ready);
const duration = await page.evaluate(() => window.DURATION);

const ff = spawn('ffmpeg', ['-y', '-loglevel', 'error', '-f', 'image2pipe', '-framerate', String(fps),
  '-c:v', 'png', '-i', '-', '-c:v', 'libx264', '-crf', '18', '-pix_fmt', 'yuv420p',
  '-movflags', '+faststart', out], { stdio: ['pipe', 'inherit', 'inherit'] });
const done = new Promise((ok, fail) => ff.on('close', c => (c === 0 ? ok() : fail(new Error('ffmpeg ' + c)))));

const t0 = Date.now(), frames = Math.round(duration * fps);
for (let i = 0; i < frames; i++) {
  await page.evaluate(([t, i]) => window.renderFrame(t, i), [i / fps, i]);   // draw exactly frame i
  const png = await page.screenshot({ type: 'png' });
  if (!ff.stdin.write(png)) await new Promise(r => ff.stdin.once('drain', r));
}
ff.stdin.end();
await done;
await browser.close();
console.log(`${frames} frames in ${((Date.now() - t0) / 1000).toFixed(1)} s -> ${out}`);
