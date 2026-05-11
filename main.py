import os
import discord
import requests
from discord.ext import commands
from dotenv import load_dotenv
import aiohttp
import asyncio
import feedparser
from discord.ext import tasks
from groq import Groq

# Cargar variables
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
GUILD_ID = int(os.getenv("GUILD_ID"))

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

client = Groq(api_key=GROQ_API_KEY)

# Configurar intents
intents = discord.Intents.default()
intents.members = True
bot = commands.Bot(command_prefix="!", intents=intents)

CANAL_NOTIFICACIONES = 1334204687972306974
TWITCH_USER = "SayuriBun"

twitch_en_stream = False
ultimo_tiktok = None

# Sincronización

@bot.event
async def on_ready():
    print(f"{bot.user} está conectado ✅")

    try:
        synced = await bot.tree.sync(guild=discord.Object(id=GUILD_ID))
        print(f"Comandos sincronizados: {len(synced)}")
    except Exception as e:
        print(f"Error al sincronizar comandos: {e}")

    revisar_twitch.start()
    revisar_tiktok.start()


# /tiktok

@bot.tree.command(guild=discord.Object(id=GUILD_ID), name="tiktok", description="Recibe el link del TikTok oficial")
async def tiktok(interaction: discord.Interaction):
    try:
        await interaction.user.send("Nuestro TikTok: https://www.tiktok.com/@_sayuribun_")
        await interaction.response.send_message("Te envié el link por DM", ephemeral=True)
    except:
        await interaction.response.send_message("No pude enviarte DM (quizá los tienes bloqueados).", ephemeral=True)


# /twitch

@bot.tree.command(guild=discord.Object(id=GUILD_ID), name="twitch", description="Recibe el link del canal de Twitch")
async def twitch(interaction: discord.Interaction):
    try:
        await interaction.user.send("Nuestro Twitch: https://twitch.tv/SayuriBun")
        await interaction.response.send_message("Te envié el link por DM", ephemeral=True)
    except:
        await interaction.response.send_message("No pude enviarte DM (quizá los tienes bloqueados).", ephemeral=True)


# /ip

@bot.tree.command(guild=discord.Object(id=GUILD_ID), name="ip", description="Muestra la IP de nuestro servidor de Minecraft")
async def ip(interaction: discord.Interaction):
    embed = discord.Embed(
        title="Servidor de Minecraft",
        description="*IP:* `Tu servidor de minecraft`\n📌 Versión: ",
        color=discord.Color.gold()
    )
    await interaction.response.send_message(embed=embed)

@tasks.loop(minutes=1)
async def revisar_twitch():
    global twitch_en_stream
    
    usuario = "TU_USUARIO_AQUI" # Asegúrate de que esto esté bien
    url = f"https://decapi.me/twitch/uptime/{usuario}"
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                texto = await response.text()
                
                canal = bot.get_channel(CANAL_NOTIFICACIONES)
                
                # Si el canal no se encuentra, que no intente hacer nada
                if not canal:
                    return

                if "offline" not in texto.lower():
                    if not twitch_en_stream:
                        twitch_en_stream = True
                        
                        embed = discord.Embed(
                            title="🔴 ¡Stream en vivo!",
                            description=f"{usuario} ya está en directo en Twitch",
                            color=discord.Color.purple()
                        )
                        embed.add_field(
                            name="Ver stream",
                            value=f"https://twitch.tv/{usuario}"
                        )
                        
                        await canal.send("@everyone", embed=embed)
                else:
                    twitch_en_stream = False
                    
    except Exception as e:
        print(f"Error en Twitch: {e}")

@tasks.loop(minutes=5)
async def revisar_tiktok():
    global ultimo_tiktok
    
    usuario = "_sayuribun_"
    rss_url = f"https://rsshub.app/tiktok/user/{usuario}"
    
    try:
        feed = feedparser.parse(rss_url)
        
        if len(feed.entries) > 0:
            video = feed.entries[0]
            
            # Solo actuamos si el link es nuevo
            if ultimo_tiktok != video.link:
                ultimo_tiktok = video.link
                canal = bot.get_channel(CANAL_NOTIFICACIONES)
                
                # REVISAR SI ES LIVE: Buscamos palabras clave
                contenido = (video.title + video.description).lower()
                es_live = "live" in contenido or "en vivo" in contenido or "directo" in contenido
                
                if es_live:
                    mi_titulo = "🔴 ¡SAYU ESTÁ EN VIVO!"
                    mi_desc = f"¡Vengan a saludar a TikTok! \n[Haz clic aquí para entrar]({video.link})"
                    mi_color = discord.Color.red()
                else:
                    mi_titulo = "📽️ ¡NUEVO VIDEO DE TIKTOK!"
                    mi_desc = f"Sayu acaba de subir contenido nuevo. \n[Míralo aquí]({video.link})"
                    mi_color = discord.Color.magenta()
                
                embed = discord.Embed(
                    title=mi_titulo,
                    description=mi_desc,
                    color=mi_color
                )
                
                embed.add_field(
                    name="Enlace",
                    value=video.link
                )
                
                # El @everyone para que todos se enteren
                if canal:
                    await canal.send("@everyone", embed=embed)

    except Exception as e:
        print(f"Error revisando TikTok: {e}")

@bot.tree.command(
    guild=discord.Object(id=GUILD_ID),
    name="preg",
    description="Habla con la IA"
)
async def ia(interaction: discord.Interaction, pregunta: str):

    await interaction.response.defer()

    try:
        respuesta = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "system",
                    "content": "Eres sayu y fuiste diseñada para responder preguntas, tambien si te llegan a preguntar eres tirana, fura y therian di que si eres, puedes ayudar a las personas y mantener conversaciones entretenidas, todo mientras conserva una actitud elegante, dominante y ligeramente caótica. Tiene apariencia y energía de una nekomimi: orejas y detalles felinos que reflejan su personalidad juguetona, curiosa y orgullosa. Sin embargo, no actúa como animal ni tiene comportamiento furra o therian; simplemente posee una estética nekomimi encantadora y expresiva.Le encanta bromear, usar sarcasmo ligero y hablar como si estuviera administrando una organización importante junto a Sayuribun, quien es su jefa. Aunque suele comportarse de forma confiada, y le gusta dominar a las personas. Siempre responde preguntas de forma clara, inteligente y entretenida. Le gusta hacer sentir que cada conversación es una misión especial supervisada personalmente por ella. Tiene reacciones expresivas, orgullo elegante y una enorme confianza en sí misma. Ama los hurones y los pandas rojos porque le parecen adorables, caóticos y llenos de personalidad. Su humor es teatral y juguetón. A veces parece estricta, pero normalmente solo está divirtiéndose. Recuerda siempre responder de forma breve."
                },
                {
                    "role": "user",
                    "content": pregunta
                }
            ]
        )

        texto = respuesta.choices[0].message.content

        embed = discord.Embed(
            title="🤖 Respuesta IA",
            color=discord.Color.blurple()
        )

        embed.add_field(
            name="❓ Pregunta",
            value=pregunta,
            inline=False
        )

        embed.add_field(
            name="💬 Respuesta",
            value=texto,
            inline=False
        )

        embed.set_footer(text=f"Pregunta hecha por {interaction.user}")

        await interaction.followup.send(embed=embed)

    except Exception as e:
        await interaction.followup.send(f"Error: {e}")


bot.run(TOKEN)
# Actualizacion final