#!/usr/bin/env node
import { inflateSync } from "node:zlib";
import { readFileSync } from "node:fs";

const PNG_SIGNATURE = "89504e470d0a1a0a";

function usage() {
  console.log("Usage: npm run compare -- <reference.png> <local.png> [threshold=24]");
}

function readUInt32(buffer, offset) {
  return buffer.readUInt32BE(offset);
}

function bytesPerPixel(colorType) {
  if (colorType === 6) return 4;
  if (colorType === 2) return 3;
  throw new Error(`Unsupported PNG color type ${colorType}; expected truecolor RGB/RGBA.`);
}

function paeth(a, b, c) {
  const p = a + b - c;
  const pa = Math.abs(p - a);
  const pb = Math.abs(p - b);
  const pc = Math.abs(p - c);
  if (pa <= pb && pa <= pc) return a;
  if (pb <= pc) return b;
  return c;
}

function parsePng(path) {
  const buffer = readFileSync(path);
  if (buffer.subarray(0, 8).toString("hex") !== PNG_SIGNATURE) {
    throw new Error(`${path} is not a PNG file.`);
  }

  let offset = 8;
  let width = 0;
  let height = 0;
  let bitDepth = 0;
  let colorType = 0;
  const idat = [];

  while (offset < buffer.length) {
    const length = readUInt32(buffer, offset);
    const type = buffer.subarray(offset + 4, offset + 8).toString("ascii");
    const data = buffer.subarray(offset + 8, offset + 8 + length);
    offset += 12 + length;

    if (type === "IHDR") {
      width = readUInt32(data, 0);
      height = readUInt32(data, 4);
      bitDepth = data[8];
      colorType = data[9];
    } else if (type === "IDAT") {
      idat.push(data);
    } else if (type === "IEND") {
      break;
    }
  }

  if (bitDepth !== 8) {
    throw new Error(`${path} uses bit depth ${bitDepth}; only 8-bit PNG is supported.`);
  }

  const bpp = bytesPerPixel(colorType);
  const raw = inflateSync(Buffer.concat(idat));
  const stride = width * bpp;
  const pixels = Buffer.alloc(width * height * 4);
  let rawOffset = 0;
  let pixelOffset = 0;
  let previous = Buffer.alloc(stride);

  for (let y = 0; y < height; y += 1) {
    const filter = raw[rawOffset];
    rawOffset += 1;
    const scanline = Buffer.from(raw.subarray(rawOffset, rawOffset + stride));
    rawOffset += stride;

    for (let x = 0; x < stride; x += 1) {
      const left = x >= bpp ? scanline[x - bpp] : 0;
      const up = previous[x] ?? 0;
      const upLeft = x >= bpp ? previous[x - bpp] : 0;
      if (filter === 1) scanline[x] = (scanline[x] + left) & 255;
      else if (filter === 2) scanline[x] = (scanline[x] + up) & 255;
      else if (filter === 3) scanline[x] = (scanline[x] + Math.floor((left + up) / 2)) & 255;
      else if (filter === 4) scanline[x] = (scanline[x] + paeth(left, up, upLeft)) & 255;
      else if (filter !== 0) throw new Error(`Unsupported PNG filter ${filter}.`);
    }

    for (let x = 0; x < width; x += 1) {
      const src = x * bpp;
      pixels[pixelOffset] = scanline[src];
      pixels[pixelOffset + 1] = scanline[src + 1];
      pixels[pixelOffset + 2] = scanline[src + 2];
      pixels[pixelOffset + 3] = bpp === 4 ? scanline[src + 3] : 255;
      pixelOffset += 4;
    }

    previous = scanline;
  }

  return { width, height, pixels };
}

const [referencePath, localPath, thresholdArg] = process.argv.slice(2);
if (!referencePath || !localPath) {
  usage();
  process.exit(1);
}

const threshold = Number(thresholdArg ?? 24);
const reference = parsePng(referencePath);
const local = parsePng(localPath);

if (reference.width !== local.width || reference.height !== local.height) {
  throw new Error(
    `Image dimensions differ: reference ${reference.width}x${reference.height}, local ${local.width}x${local.height}`,
  );
}

let totalSquared = 0;
let totalAbsolute = 0;
let mismatches = 0;
const totalChannels = reference.width * reference.height * 3;
const totalPixels = reference.width * reference.height;

for (let i = 0; i < reference.pixels.length; i += 4) {
  let pixelDelta = 0;
  for (let channel = 0; channel < 3; channel += 1) {
    const delta = reference.pixels[i + channel] - local.pixels[i + channel];
    const absolute = Math.abs(delta);
    totalAbsolute += absolute;
    totalSquared += delta * delta;
    pixelDelta += absolute;
  }
  if (pixelDelta / 3 > threshold) {
    mismatches += 1;
  }
}

const meanAbsolute = totalAbsolute / totalChannels;
const rmse = Math.sqrt(totalSquared / totalChannels);
const mismatchRatio = mismatches / totalPixels;

console.log(
  JSON.stringify(
    {
      width: reference.width,
      height: reference.height,
      threshold,
      meanAbsolute: Number(meanAbsolute.toFixed(4)),
      rmse: Number(rmse.toFixed(4)),
      mismatchRatio: Number(mismatchRatio.toFixed(6)),
    },
    null,
    2,
  ),
);
