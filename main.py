from flask import Flask, render_template, request, jsonify
import json
import openpyxl
import random
import string
from discord.ext import commands

# Load config
with open('config.json', 'r') as config_file:
    config = json.load(config_file)

app = Flask(__name__)

# Discord bot setup
bot_token = config["discord"]["bot_token"]
server_id = int(config["discord"]["server_id"])
role_id = int(config["discord"]["role_id"])
bot = commands.Bot(command_prefix='/')

@app.route('/')
def index():
    return render_template('index.html', questions=config['questions'])

@app.route('/submit', methods=['POST'])
def submit():
    data = request.form.to_dict()
    
    # Validation
    for question in config['questions']:
        if question['required'] and not data.get(question['id']):
            return jsonify({"success": False, "message": f"{question['label']} kötelező!"})

    # Save to Excel
    file_name = config['output_file']
    wb = openpyxl.Workbook()
    ws = wb.active

    if not ws.max_row > 1:
        ws.append([q['label'] for q in config['questions']])

    ws.append([data[q['id']] for q in config['questions']])
    wb.save(file_name)

    # Generate unique code
    unique_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))

    return jsonify({"success": True, "code": unique_code})

@bot.command(name="összekötés")
async def osszekotes(ctx, code: str):
    # Logic to validate the code and assign role
    member = ctx.guild.get_member(ctx.author.id)
    role = ctx.guild.get_role(role_id)
    await member.add_roles(role)
    await member.edit(nick=code)
    await ctx.send("Sikeres összekötés!")

if __name__ == '__main__':
    app.run(debug=True)
