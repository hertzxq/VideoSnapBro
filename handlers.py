from aiogram.filters import Command, StateFilter
from aiogram.types import Message, FSInputFile, ReplyKeyboardMarkup, KeyboardButton
from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
import os
from yt_handler import download_video, logger, find_video_by_id

router = Router()

class DownloadStates(StatesGroup):
    waiting_for_url = State()

def get_main_keyboard():
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📥 Загрузить видео")],
        ],
        resize_keyboard=True,
        one_time_keyboard=False
    )
    return keyboard

@router.message(Command('start'))
async def send_welcome(message: Message):
    await message.answer(
        'Привет! Я бот для загрузки видео (YouTube, ВК и т.д.)\nДля загрузки нажми на кнопку ниже!',
        reply_markup=get_main_keyboard()
    )

@router.message(Command('download'))
async def cmd_download(message: Message, state: FSMContext):
    await message.answer('Отправь прямую ссылку на видео!', reply_markup=get_main_keyboard())
    await state.set_state(DownloadStates.waiting_for_url)

@router.message(F.text == '📥 Загрузить видео')
async def prompt_url(message: Message, state: FSMContext):
    await message.answer('Отправь прямую ссылку на видео!', reply_markup=get_main_keyboard())
    await state.set_state(DownloadStates.waiting_for_url)

@router.message(StateFilter(DownloadStates.waiting_for_url))
async def take_url(message: Message, state: FSMContext):
    url = message.text
    try:
        await message.answer("Отлично, уже ищу видео!", reply_markup=get_main_keyboard())
        
        video_info = download_video(url, output_path='videos')
        await message.answer('Видео скачано, скоро отправлю!', reply_markup=get_main_keyboard())
        
        video_path = find_video_by_id(video_info['id'], output_path='videos')
        if video_path and os.path.exists(video_path):
            video = FSInputFile(video_path)
            await message.answer_video(video, caption='А вот и ваше видео!', reply_markup=get_main_keyboard())
            
            try:
                os.remove(video_path)
                logger.info(f"Файл {video_path} успешно удалён")
            except FileNotFoundError:
                logger.error(f"Файл {video_path} не найден для удаления")
            except PermissionError:
                logger.error(f"Нет прав для удаления файла {video_path}")
            except Exception as e:
                logger.error(f"Ошибка при удалении файла {video_path}: {str(e)}")
        else:
            logger.error(f"Video file not found: {video_path}")
            await message.answer('Видео не найдено! :(', reply_markup=get_main_keyboard())
            
            os.remove(video_path)
            logger.info(f"Файл {video_path} успешно удалён")
        
        await state.clear()
    except Exception as e:
        logger.error(f"Error processing video: {str(e)}")
        await message.answer(f'Слишком большой размер видео!', reply_markup=get_main_keyboard())
        
        os.remove(video_path)
        logger.info(f"Файл {video_path} успешно удалён")
        
        await state.clear()