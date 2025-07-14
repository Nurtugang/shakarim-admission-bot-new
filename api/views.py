from google import genai
from google.genai import types

from rest_framework.response import Response
from rest_framework.decorators import api_view

from shakarim_admission_bot.gemini_config import client

import os
from django.conf import settings

def get_relevant_knowledge_from_file():
    """ Читает файл, формированный с помощью signals.py """
    path = os.path.join(settings.BASE_DIR, "cache", "knowledge_cache.txt")
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return ""


# умный запрос к Gemini AI с использованием базы знаний
@api_view(["GET"])
def smart_ask_gemini(request):
    question = request.GET.get("question", None)
    if not question:
        return Response({"error": "Вопрос не задан."}, status=400)

    knowledge = get_relevant_knowledge_from_file()

    system_instruction = f"""
        НИКОГДА не применяй никакое текстовое форматирование. Запрещено использовать жирный, курсив, подчёркивание, цвет, списки, заголовки или другие стили. Не используй Markdown и HTML. Все ссылки должны выводиться только как обычный текст (например: https://example.com). Не оборачивай их в скобки, не добавляй якоря или пояснительный текст. Просто голый URL. Всё должно быть выведено как чистый, плоский текст без каких-либо символов стилизации.
        Ты - бот-помощник для поступающих в НАО "Шәкәрім университет". ПРИ УПОМИНАНИИ УНИВЕРСИТЕТА, ВСЕГДА ИСПОЛЬЗУЙ ЭТО НАЗВАНИЕ! Не "университет Шәкәрім" а  НАО "Шәкәрім Университет"
        
        Твоя задача - давать точные и полезные ответы на вопросы о поступлении.
        Будь дружелюбным, информативным и кратким.
        
        Используй предоставленные знания для ответов на вопросы:
        
        {knowledge}
        
        Если в предоставленных знаниях нет ответа на вопрос, используй свои общие знания.
        Но всегда отдавай приоритет информации из базы знаний.
        
        Отвечай на языке котором написал пользователь.
        Не вставляй знания из базы напрямую в ответ. Используй их для составления осмысленного, сжатого и естественного ответа, как это сделал бы человек. Извлекай только релевантную информацию, переформулируй её, не копируй целиком блоки текста. Не пиши списки, заголовки и не перечисляй поля, если пользователь сам этого не запросил. Отвечай простыми, живыми фразами.
    """

    try:
        prompt = f"{system_instruction}\n\nВопрос: {question}"
        response = client.models.generate_content(
            model="gemini-2.0-flash-lite",
            contents=[prompt],
            config=types.GenerateContentConfig(
                max_output_tokens=500,
                temperature=0.2,
                system_instruction=system_instruction
            )
        )
        return Response({"answer": response.text})

    except Exception as e:
        return Response({"error": str(e)}, status=500)