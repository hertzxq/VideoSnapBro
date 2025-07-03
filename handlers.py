from aiogram.filters import Command 
from aiogram.types import Message, FSInputFile
from aiogram import Router
import os
from yt_handler import download_video, logger, find_video_by_id

router = Router()

@router.message(Command('start'))
async def send_welcome(message: Message):
    await message.answer('Привет, напиши ссылку на видео!: ')

@router.message()
async def take_url(message: Message):
    url = message.text
    try:
        await message.answer("Отлично, уже ищу видео!")
        
        video_info = download_video(url, output_path='videos')
        await message.answer('Видео скачано, Скоро отправлю!')
        
        video_path = find_video_by_id(video_info['id'], output_path='videos')
        if video_path and os.path.exists(video_path):
            video = FSInputFile(video_path)
            await message.answer_video(video, caption='А вот и ваше видео!')
            os.remove(video_path)
        else:
            logger.error(f"Video file not found: {video_path}")
            await message.answer('Видео не найдено!(')
    except Exception as e:
        logger.error(f"Error processing video: {str(e)}")