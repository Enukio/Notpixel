const { Telegraf } = require('telegraf');
const fs = require('fs');
const { spawn } = require('child_process');
require('dotenv').config();

const BOT_TOKEN = process.env.BOT_TOKEN;
if (!BOT_TOKEN) {
    console.error('Error: BOT_TOKEN is not defined in the environment variables.');
    process.exit(1);
}

const bot = new Telegraf(BOT_TOKEN);

bot.start((ctx) => {
    ctx.reply('Hello! Please paste your NotPixel Query ID.');
});

function isValidInput(input) {
    const regex = /^[a-zA-Z0-9_-]{1,100}$/;
    return regex.test(input);
}

bot.on('text', (ctx) => {
    const inputText = ctx.message.text;

    if (!isValidInput(inputText)) {
        return ctx.reply('Invalid input. Please provide a valid Query ID.');
    }

    const filePath = 'data.txt';
    try {
        fs.writeFileSync(filePath, inputText, 'utf8');
    } catch (err) {
        console.error('Error writing to file:', err);
        return ctx.reply('An error occurred while processing your input.');
    }

    ctx.reply('Processing your request. Please wait...');

    const pythonProcess = spawn('python3', ['main.py', '-a', '3'], { cwd: 'venv/bin' });

    pythonProcess.stdout.on('data', (data) => {
        const output = data.toString();
        console.log('Python Output:', output);
        ctx.reply(output.substring(0, 2000));
    });

    pythonProcess.stderr.on('data', (data) => {
        const error = data.toString();
        console.error('Python Error:', error);
        ctx.reply(`An error occurred:\n${error.substring(0, 2000)}...`);
    });

    pythonProcess.on('close', (code) => {
        ctx.reply(`Process finished with exit code ${code}.`);
    });

    const timeout = setTimeout(() => {
        if (!pythonProcess.killed) {
            pythonProcess.kill('SIGINT');
            ctx.reply('Process terminated after 3 minutes due to timeout.');
        }
    }, 180000);

    pythonProcess.on('exit', () => clearTimeout(timeout));
});

process.once('SIGINT', () => bot.stop('SIGINT'));
process.once('SIGTERM', () => bot.stop('SIGTERM'));

bot.launch();
