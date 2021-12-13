from io import BytesIO
from Natsunagi import aiohttpsession


async def make_carbon(code):
    url = "https://carbonara.vercel.app/api/cook"
    async with aiohttpsession.post(url, json={"code": code}) as resp:
        image = BytesIO(await resp.read())
    image.name = "Natsunagi_Carbon.png"
    return image
