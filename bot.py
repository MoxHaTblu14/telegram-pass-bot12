
import logging
import uuid
import os
import yagmail
import asyncio
from weasyprint import HTML
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command

logging.basicConfig(level=logging.INFO)

EMAIL_ADDRESS = 'berezyukov01@bk.ru'
EMAIL_PASSWORD = 'Yw0sksMVnug1y8c13jdj'
RECIPIENT_EMAIL = 'berezyukovda@gmail.com'
API_TOKEN = '7667707824:AAE7fLizOwpdThAnGdOUwjYF9SYOy0hgX1Y'

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

@dp.message(Command('start'))
async def start_command(message: types.Message):
    await message.answer("Привет! Я готов оформлять пропуска 🚛")

def generate_html(data, uid):
    with open("pass_template.html", "r", encoding="utf-8") as f:
        template = f.read()
    for key, value in data.items():
        template = template.replace(f"{{{{{key}}}}}", value)
    template = template.replace("{{uid}}", uid)
    return template

def save_pdf_from_html(html_content, pdf_path):
    HTML(string=html_content).write_pdf(pdf_path)
    logging.info(f"PDF сохранён в {pdf_path}")

@dp.message(Command('pass'))
async def pass_command(message: types.Message):
    try:
        args = message.text.split()
        if len(args) < 16:
            await message.answer("Недостаточно данных. Пример:
/pass 20.04.2025 Иванов Иван Иванович 01.01.1980 1234 567890 ВУ1234567 123456789012 Москва,+ул.Примерная,+1 +79161234567 Scania+А123ВС77 CONT12345 ООО+Поставщик Москва,+Россия Товар:Телевизоры-10шт")
            return

        data = {
            "Дата заезда": args[0],
            "ФИО": ' '.join(args[1:4]),
            "Дата рождения": args[4],
            "Паспорт": f"{args[5]} {args[6]}",
            "ВУ": args[7],
            "ИНН": args[8],
            "Адрес": args[9].replace('+', ' '),
            "Телефон": args[10],
            "Машина": args[11].replace('+', ' '),
            "Контейнер": args[12],
            "Поставщик": args[13].replace('+', ' '),
            "Город": args[14].replace('+', ' '),
            "Товар": ' '.join(args[15:]).replace('+', ' ')
        }

        uid = uuid.uuid4().hex
        output_dir = "output"
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        pdf_path = f"{output_dir}/pass_{uid}.pdf"
        html_content = generate_html(data, uid)
        save_pdf_from_html(html_content, pdf_path)

        yag = yagmail.SMTP(
            user=EMAIL_ADDRESS,
            password=EMAIL_PASSWORD,
            host='smtp.mail.ru',
            port=465,
            smtp_ssl=True
        )

        yag.send(
            to=RECIPIENT_EMAIL,
            subject="Пропуск",
            contents="Пропуск во вложении.",
            attachments=[pdf_path]
        )

        await message.answer("Пропуск оформлен и отправлен на почту 📧")

    except Exception as e:
        await message.answer(f"Ошибка при оформлении пропуска: {e}")
        logging.error(f"Ошибка: {e}")

async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
