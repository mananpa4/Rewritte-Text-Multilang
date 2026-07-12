// const fetch = require('node-fetch'); // Native fetch is available
// Actually in Node 18+ fetch is global.
const iconv = require('iconv-lite');

async function probe() {
    const res = await fetch('https://www.kekenet.com/grammar/0101.htm', {
        headers: { 'User-Agent': 'Mozilla/5.0' }
    });
    const buffer = await res.arrayBuffer();
    const html = iconv.decode(Buffer.from(buffer), 'gbk');
    console.log(html.slice(0, 5000)); // Print first 5000 chars
}

probe();
