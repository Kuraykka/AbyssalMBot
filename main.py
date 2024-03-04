import discord
from discord.ext import commands, tasks
import re
import requests
from discord.utils import get
import discord.utils
import asyncio


BOT_PREFIX = "!"
SERVER_IP = "45.126.208.108:19133"
MCS_VSTATS_API = f"https://api.mcsrvstat.us/3/45.126.208.108:19133"
id_category = 1213857463619690516
id_channel_ticket_logs = 1213857614212104306
id_staff_role = 1206249216775553055
embed_color = 0xfcd005
categoria_tickets_id = 1213971752628129872
tickets_anteriores = 0
ROL_STAFF_ID = 1213552200857681958
CATEGORIA_PERMITIDA_ID = 1213971752628129872

advertencias = {} 


intents = discord.Intents.all()
intents.presences = True

bot = commands.Bot(command_prefix=BOT_PREFIX, intents=intents)

@bot.event
async def on_ready():
    print(f'Bot conectado como {bot.user.name}')

discord_invite_pattern = re.compile(r"(discord\.gg/|discord\.com/invite/)[a-zA-Z0-9]+")

@bot.event
async def on_message(message):

    if message.content.startswith('!write'):
        await bot.process_commands(message)
    else:

        if (
            discord.utils.get(message.author.roles, name="DEV-DC") and
            (discord_invite_pattern.search(message.content) or any(word in message.content for word in ["http", "www.", ".com", ".net", ".org"]))
        ):

            await message.delete()
            await message.channel.send(f"{message.author.mention}, solo los usuarios con el rol 'DEV-DC' pueden enviar invitaciones o enlaces web aquí.")
        else:

            await bot.process_commands(message)

@bot.command()
async def write(ctx, *, mensaje):

    babilonia_role = discord.utils.get(ctx.guild.roles, name="DEV-DC")

    if babilonia_role in ctx.author.roles:

        await ctx.message.delete()

        embed = discord.Embed(
            title='🚀 AbyssalMC',
            description=mensaje,
            color=discord.Color.blue()
        )
        await ctx.send(embed=embed)
    else:
        await ctx.send("No tienes el rol 'DEV-DC' para ejecutar este comando.")

@bot.command()
async def ip(ctx):
    try:
        response = requests.get(MCS_VSTATS_API)

        if response.status_code == 200 and 'application/json' in response.headers.get('content-type'):
            data = response.json()

            if "error" not in data:
                server_name = data.get("hostname", "AbyssalMC")
                players_online = data.get("players", {}).get("online", "Desconocido")
                motd = data.get("motd", {}).get("clean", "Desconocido")
                version = data.get("version", "Desconocido")

                embed = discord.Embed(
                    title=f"Información de 🚀 AbyssalMC",
                    description=f"🌐 IP: {SERVER_IP}\n🌟 Número de jugadores: {players_online}\n🎉 MOTD: {motd}\n🌺 Versión: {version}",
                    color=discord.Color.blue()
                )

                await ctx.send(embed=embed)
            else:
                await ctx.send(f"No se pudo obtener la información del servidor. Error de la API: {data['error']}")
        else:
            await ctx.send(f"No se pudo obtener la información del servidor. Respuesta de la API no es JSON válido.")

    except requests.RequestException as e:
        print(f"Error de solicitud: {str(e)}")
        await ctx.send(f"Ocurrió un error al procesar la solicitud: {str(e)}")

@bot.event
async def on_member_join(member):
    
    rol_usuario_id = 1213552200782188582 

    
    rol_usuario = member.guild.get_role(rol_usuario_id)

    
    if rol_usuario and rol_usuario not in member.roles:
        
        await member.add_roles(rol_usuario)
        print(f"Rol '{rol_usuario.name}' asignado a {member.display_name}")

    
    channel_id = 1213948694202941482  
    channel = bot.get_channel(channel_id)

    if channel:
     mensaje_bienvenida = (
        f"Un nuevo usuario entró {member.mention}!\n\n"
        f"¡Hey! 😳 Te has unido al servidor de Discord oficial de AbyssalMC. Aquí tienes información sobre algunos canales importantes:\n\n"
        f"1. **<#{1213563399728799795}>**: Asegúrate de revisar las reglas específicas del servidor de Minecraft en este canal.\n"
        f"2. **<#{1213953578671153262}>**: Lee las reglas generales y normas del servidor de Discord en este canal.\n"
        f"3. **<#{1213563008148836473}>**: Mantente actualizado con los anuncios y noticias importantes en este canal.\n\n"
        f"Gracias a ti ahora somos {len(member.guild.members)} usuarios.\n\n"
        f"👀 | Somos lo que ves. ¡Tu servidor favorito!"
    )

    
    await channel.send(mensaje_bienvenida)

@bot.event
async def on_ready():
    print(f'Bot conectado como {bot.user.name}')
   
    update_status.start()

def contar_tickets():
    global categoria_tickets_id
    
    categoria_tickets = bot.get_channel(categoria_tickets_id)

    if categoria_tickets and isinstance(categoria_tickets, discord.CategoryChannel):
       
        return len(categoria_tickets.channels)
    return 0

@tasks.loop(seconds=10)
async def update_status():
    global tickets_anteriores
    cantidad_canales = contar_tickets()

   
    if cantidad_canales != tickets_anteriores:
        estado = discord.Game(name=f"Viendo {cantidad_canales} {'ticket' if cantidad_canales == 1 else 'tickets'}")
        await bot.change_presence(activity=estado)
        tickets_anteriores = cantidad_canales

@bot.command(name='staff')
async def staff(ctx):
    
    if ctx.channel.category.id != CATEGORIA_PERMITIDA_ID:
        await ctx.send("Este comando solo puede ser ejecutado en la categoría permitida.")
        return

    usuario = ctx.author.display_name
    rol_staff = ctx.guild.get_role(ROL_STAFF_ID)

    
    advertencias[ctx.author.id] = advertencias.get(ctx.author.id, 0) + 1

    await ctx.send(f"{rol_staff.mention}, {usuario} ha solicitado ayuda. ¡Por favor, asiste!")

mensaje_verificacion = None
tu_id = 776884983423303720

@bot.event
async def on_ready():
    print(f'Bot conectado como {bot.user.name}')

@bot.event
async def on_raw_reaction_add(payload):
    global mensaje_verificacion 

    if mensaje_verificacion is not None and payload.emoji.name == '✅' and payload.message_id == mensaje_verificacion.id:
        guild = bot.get_guild(payload.guild_id)
        member = guild.get_member(payload.user_id)

        if member:
            rol_a_asignar = guild.get_role(1214200603631427626)

            embed_asignacion = discord.Embed(
                title="Asignación de Rol",
                description=f"Se asignó el rol {rol_a_asignar.name} a {member.display_name}.",
                color=discord.Color.green()
            )

            canal_logs = bot.get_channel(1214210188740005908) 
            await canal_logs.send(embed=embed_asignacion)

            await member.add_roles(rol_a_asignar)

@bot.command(name='verificacion')
async def verificacion(ctx):
    global mensaje_verificacion 

    if ctx.author.id == tu_id:
        embed_verificacion = discord.Embed(
            title="Verificación",
            description="Para acceder al servidor debes reaccionar al emoji ✅.",
            color=discord.Color.blue()
        )

        mensaje_verificacion = await ctx.send(embed=embed_verificacion)
        await mensaje_verificacion.add_reaction('✅')
    else:
        await ctx.send("Solo el propietario del bot puede ejecutar este comando.")

@bot.event
async def on_raw_reaction_add(payload):
    global mensaje_verificacion 

    print(f"Emoji: {payload.emoji.name}")
    print(f"Message ID: {payload.message_id}")

    if mensaje_verificacion is not None and payload.emoji.name == '✅' and payload.message_id == mensaje_verificacion.id:
        guild = bot.get_guild(payload.guild_id)
        member = guild.get_member(payload.user_id)

        print(f"Guild: {guild}")
        print(f"Member: {member}")

        if member:
            rol_a_asignar = guild.get_role(1214200603631427626)

            print(f"Role to assign: {rol_a_asignar}")

            embed_asignacion = discord.Embed(
                title="Asignación de Rol",
                description=f"Se asignó el rol {rol_a_asignar.name} a {member.display_name}.",
                color=discord.Color.green()
            )

            canal_logs = bot.get_channel(1214210188740005908) 
            await canal_logs.send(embed=embed_asignacion)

            await member.add_roles(rol_a_asignar)

        else:
            print("Member not found")
          

@bot.command(name='serverinfo')
async def serverinfo(ctx):
    guild = ctx.guild
   
    embed = discord.Embed(
        title=f"🌐 Información del Servidor - {guild.name}",
        description=f"**ID:** {guild.id}",
        color=discord.Color.blue()
    )

    if guild.icon:
        embed.set_thumbnail(url=guild.icon.url)

    embed.add_field(name="👑 Propietario", value=f"{guild.owner.name}#{guild.owner.discriminator}", inline=True)
    embed.add_field(name="👥 Miembros", value=guild.member_count, inline=True)
    embed.add_field(name="🔒 Roles", value=len(guild.roles), inline=True)
    embed.add_field(name="💬 Canales de Texto", value=len(guild.text_channels), inline=True)
    embed.add_field(name="🔊 Canales de Voz", value=len(guild.voice_channels), inline=True)
    embed.set_footer(text=f"📅 Creado el {guild.created_at.strftime('%d-%m-%Y')}")

    await ctx.send(embed=embed)



bot.run('MTIxMDkxMDg4MDI4NDI4MjkwMA.GAcoRP.WQR0gEnMUgtpOnsyGsdYENhxGVSVz_XAoME49A')
