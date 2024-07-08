[# Бот для Telegram-канала "[Код на салфетке](https://t.me/press_any_button)" и чата "[Кот на салфетке](https://t.me/pressanybutton_chat)"

## О репозитории
Репозиторий с исходным кодом бота для конкурса начинающих программистов на Python

## Задача
У нас есть "Бот на салфетке" - бот для канала и чата. В связи с большим количеством спамеров, приходящих в чат и
спамящих своим "очень интересным предложением", возникла необходимость в защите - введением проверки новых пользователей
чата через "капчу", при правильном ответе на которую пользователь может продолжить общаться, в противном случае бот
исключает его из чата.

Способов решения задачи несколько, от чего она является идеальной для конкурса.

### Необходимо:
1. Реализовать "капчу" для нового участника чата.
2. "Капча" должна быть в виде изображения.
3. Для упрощения, достаточно реализовать задачу на сложение, результат которой будет проверять бот.
4. Дать пользователю три попытки на решение задачи.
5. Если пользователь три раза вводит неверный ответ - исключение из чата.
6. Все сообщения пользователя без верного ответа - удалять.
7. (Опционально) Добавить таймер в течении которого пользователь должен ответить верно (включая неверные ответы), если
   не было верного ответа или не было сообщений вовсе - исключение.

## Что было сделано?
1. Создан fork проекта
2. Изучена структура предложенного чат-бота. В рамках исследования выявлено, что при входе в чат новым пользователем,
система совершает ряд запросов, это отражается в функциях: `on_user_join` в файле `events.py`, а также `about_message`
в файле `views.py`
3. Для того, чтобы при добавлении нового пользователя в чат проводилась проверка (анти-спам) в соответствии с условиями
задачи было принято решение создать файл `check_captcha.py`, в который я поместил основной функционал обработки условий 
при прохождении проверки, а именно:
4. Определена функция `generate_captcha()`, в которой содержится логика создания изображений для прохождения 
captcha-проверок.
     
   В этой функции мы можем корректировать принцип генерации уравнения, в данном случае, в соответствии с 
условиями задачи уравнение представляет собой сложение в одно действие:
    ```    
    num1 = random.randint(1, 9)
    num2 = random.randint(1, 9)
    result = num1 + num2
    ```
   В части генерации изображения мы также можем корректировать размеры, к сожалению, улучшение качества происходит 
только посредством увеличения размера изображения, т.к. не нашел как прикрутить dpi
    ```       
        # Создание изображения капчи
    img = Image.new('RGB', (400, 160), color=(255, 255, 255))
    d = ImageDraw.Draw(img)
   ```
   После определения размеров изображения мы можем выбрать шрифт (я решил использовать стандартный) и указать положение 
текста на созданном изображении. Размер шрифта определяется при вызове `ImageFont.load_default()` - в данном случае
это значение равно 90 единиц. А расположение определяется в `d.text()`
    ```
    font = ImageFont.load_default(90)
    d.text((35, 25), f"{num1} + {num2} = ?", font=font, fill=(0, 0, 0))
     ```
   Далее созданное изображение необходимо хранить для последующей отправки юзеру, мною было принято решение сохранять в
дирректории проекта в отдельной папке `captcha_images`, если ранее такой директории не было создана - система создаст 
автоматически. Единственное, что я понял на момент написания readme - надо бы удалять captcha при завершении процесса
ввода (независимо от того успешно ли прошла проверка), но есть как есть
   ```
    # Создание пути для сохранения изображения
    img_dir = 'captcha_images'
    os.makedirs(img_dir, exist_ok=True)
    img_path = os.path.join(img_dir, f"captcha_{num1}_{num2}.png")
    img.save(img_path)
   ```
   После этого система отправляет в логи сообщение о том, что капча была успешно создана и сохранена на компьютере в
указанной дирректории и возвращает изображение и результат ожидаемой операции, чтобы в дальнейшем знать с чем сравнивать
   ```
    logger.info(f"Капча сгенерирована: {num1} + {num2} = {result}, сохранена в {img_path}")

    return img_path, result
   ```

    - Определена функция send_captcha(), в которой содержится логика отправки капчи новому пользователю, а также запуск 
таймера из функции `check_captcha_timeouts()`. Для данной функции определены следующие аргументы: `bot: Bot, chat_id: int,
user_id: int, first_name: str)`, `bot` нужен для корректной работы функции `test_captcha()`, `chat_id` для определения 
группы, в которой должна проводится проверка, `user_id` для определения лица, которое проходит проверку и `first_name` 
для красоты обращения к таком лицу.  
   UPD: Могут возникнуть проблемы, если у пользователя нет `first_name` или он скрыт, но в момент разработки не было
возможности проверить поведение системы при таких условиях.  
   Сама функция определяет переменные `img_path` - дирректорию и `result` - то, чему должен соответствовать идеальный ответ
пользователя на основе результата функции `generate_captcha()`, которое мы получаем в конце через `return img_path, result`
   
   ```   
        img_path, result = generate_captcha()
   ```
   Далее мы создаем словарь, к которому будем обращаться для проверки результата, сравнения и обновления данных о
предупреждениях, полученных пользователем в случае неудачного ответа, а также времени начала отсчета таймера, полученного
ответа от пользователя, а также его `first_name` (это для красоты, помним)
   ```
   users_data[user_id] = {
        'result': result,
        'attempts': 0,
        'start_time': time.time(),
        'captcha_message_id': None,
        'first_name': first_name  # Сохранение first_name
    }
   ```
   Далее мы определяем переменную `photo` и указываем путь к нашей капче.
   ```
    photo = FSInputFile(img_path)
   ```
   После мы определяем `caption`, в которой сообщаем пользователю о необходимости пройти проверку и рассказываем об
условиях ее прохождения:
   ```
    caption = (f"{first_name}, приветствуем!\n\nРеши пожалуйста это уравнение, "
               f"чтобы убедиться, что ты не бот.\n\nНа решение тебе дается "
               f"1 минута и 3 попытки")
   ```
   Далее мы определяем переменную `sent_message`, в которой дожидаемся корутины с фотографией в нужный чат, с нужным
текстом инструкции:
   ```
    sent_message = await bot.send_photo(chat_id, photo, caption=caption)
   ```
   Далее мы обновляем наш словарь `users_data` и заносим туда данные с уже известным `captcha_message_id`:
   ```    
   users_data[user_id]['captcha_message_id'] = sent_message.message_id
   ```
   После того как мы отправили капчу пользователю, система делает соответствующую пометку в логах:
   ```    
   logger.info(f"Капча отправлена {user_id} в чат {chat_id}")
   ```    
   Теперь, когда пользователь получил свое задание, нам необходимо начать проверять исполнение озвученных условий,
здесь мы начнем отсчитывать таймер для функции `check_captcha_timeouts()`:
   ```
   asyncio.create_task(check_captcha_timeouts(bot, chat_id, user_id))
   ```
5. Определены две функции для проверки соответствия совершенных пользователем действий, согласно предъявленным 
требованиям, а именно: правильное решение предложенного уравнения должно быть отправлено пользователем в течении 1-й
минуты или в пределах 3-х попыток.  

    В целях упрощения читаемости функций проверки по этим условиям были разбиты на 2 части,а именно в функции 
`check_captcha_timeouts()` задается и проверяется общее время, отведенное пользователю на решение, а в
в функции `check_users_captcha()` проверяется корректность предложенного пользователем решения в пределах отведенного
времени.   

    Также в функции `check_users_captcha()` реализовано уведомление пользователя о неудачных попытках, количестве
оставшихся, а также времени, доступного для решения задачи. В случае, если пользователь дал неправильный ответ, то
предыдущее информационное сообщение, а также некорректный ответ пользователя удаляются. При исчерпании доступных попыток,
опреденных 
    ```
        remaining_attempts = 3 - users_data[user_id]['attempts']
        remaining_time = 60 - elapsed_time
    ```
    Но рассмотрим подробнее каждую из функций:  
5.1. `check_captcha_timeouts()` принимает следующие аргументы: `bot: Bot`, `chat_id: int`, `user_id: int`.   
Как указывалось ранее, аргумент `bot` нужен для корректной работы функции `test_captcha()`, `chat_id` для определения
группы, в рамках которой будет проводиться проверка ботом, т.к. подразумевается, что бот может быть запущен одновременно
для нескольких групп. `user_id` для определения пользователя, в отношении которого запущен таймер.

Функция обеспечивает автоматическое управление пользователями в чате, обрабатывая капчи, исключая пользователей, 
которые не выполнили задание вовремя, и корректно обрабатывая исключения, такие как попытка исключения администратора.

Для описания принципа работы этой функции разделим ее на несколько частей:  
5.1.1.  Проверка данных пользователя:
   - Функция постоянно выполняется в цикле while True. 
   - Используется текущее время current_time = time.time(). 
   - Из словаря users_data извлекаются данные о пользователе по его user_id. 
     - Если данные о пользователе существуют (if data:), то рассчитывается время, прошедшее с начала задания, и 
оставшееся время на выполнение задания.
      ```
      while True:
          current_time = time.time()
          data = users_data.get(user_id)
          if data:
              elapsed_time = current_time - data['start_time']
              remaining_time = 60 - elapsed_time
      ```
Завершение цикла происходит только в случае удаления пользователя из словаря `users_data`:
        ```
        break  # Выходим из цикла после удаления данных пользователя
        ```

5.1.2. Обработка истечения времени:
- Если прошло более 60 секунд с момента выдачи задания `(if elapsed_time > 60:)`:
  - Пытается удалить сообщение с капчей. 
  ```
                  try:
                      await bot.delete_message(chat_id, data['captcha_message_id'])
                  except Exception as e:
                      logger.warning(f"Ошибка при удалении сообщения с капчей: {e}")
   ```
- Если существует предупреждающее сообщение, в случае если пользователь ранее дал неправильный ответ, то оно также 
удаляется. Такое предупреждающее сообщение создается в функции `check_users_captcha()`

   ```                
                 if 'warning_message_id' in data:
                    try:
                        await bot.delete_message(chat_id, data['warning_message_id'])
                    except Exception as e:
                        logger.warning(f"Ошибка при удалении предупреждающего сообщения: {e}")
   ```
- Пытается забанить пользователя в чате, чтобы исключить из чата, а затем разбанить его, если пользователь по ряду
причин не смог пройти проверку (плохое интернет соединение или отвлекли или телефон разрядился и т.д.)
   ```   
                try:
                    await bot.ban_chat_member(chat_id, user_id)
                    first_name = users_data[user_id]['first_name']
   ```
- Система уведомляет чат об исключении пользователя и удаляет данные пользователя из словаря `users_data`.
   ```
                      await bot.send_message(chat_id, f"Пользователь {first_name} был исключен из чата по причине "
                                                    "истечения времени на выполнение капчи.\n\n Как думаете, вернется?")
                    users_data.pop(user_id, None)
                    logger.info(
                        f"Пользователь {user_id} был исключен из чата по причине истечения времени на выполнение капчи")
                    await bot.unban_chat_member(chat_id, user_id)  # Убираем пользователя из бана
  ```
5.1.3. Обработка ошибки при удалении администратора:
- Если попытка забанить пользователя не удалась из-за того, что пользователь является админом:
   ```
                  except Exception as e:
                    if "can't remove chat owner" in str(e):
  ```
- Пытается удалить предупреждающее сообщение, если оно существует.
   ```
                          if 'warning_message_id' in data:
                            try:
                                await bot.delete_message(chat_id, data['warning_message_id'])
                            except Exception as e:
                                logger.warning(f"Ошибка при удалении предупреждающего сообщения: {e}")
  ```
- Отправляет сообщение в чат с уведомлением, что нельзя удалять админа, и прикрепляет клавиатуру с кнопкой 
“🪄 Волшебная палочка”.
   ```
                          keyboard = InlineKeyboardMarkup(inline_keyboard=[
                            [InlineKeyboardButton(text="🪄 Волшебная палочка", callback_data='admin_warning')]
                        ])
                        sent_message = await bot.send_message(chat_id, "Кот, ну нельзя удалять админа",
                                                              reply_markup=keyboard)
  ```
- Сохраняет ID отправленного предупреждающего сообщения в данные пользователя.
   ```
                        users_data[user_id]['warning_message_id'] = sent_message.message_id
                        logger.info(f"Пользователь {user_id} попытался удалить админа в чате {chat_id}")
  ```
5.1.4. Логирование и ожидание:
  -	Логирует оставшееся время для пользователя.
   ```
               else:
                logger.info(f"Оставшееся время для пользователя {user_id}: {int(remaining_time)} секунд")
   ```
-	Ждет 5 секунд перед следующей проверкой состояния пользователей `(await asyncio.sleep(5))`

5.2. Функция `check_user_captcha()` принимает следующие аргументы: `bot: Bot`, `chat_id: int`, `user_id: int` и 
`message: types.Message`  

Как указывалось ранее, аргумент `bot` нужен для корректной работы функции `test_captcha()`, `chat_id` для определения
группы, в рамках которой будет проводиться проверка ботом, т.к. подразумевается, что бот может быть запущен одновременно
для нескольких групп. `user_id` для определения пользователя, в отношении которого производится проверка его ответов, а 
`message` для того, чтобы получать от пользователя сообщения (ответы).


Функция обеспечивает автоматическое управление пользователями в чате, обрабатывая капчи, исключая пользователей, 
которые не выполнили задание (превысели лимит допустимых попыток), и корректно обрабатывая исключения, такие как 
попытка исключения администратора, а также передавая данные дальше, если пользователь успешно прошел проверку.

Для подробного разбора этой функции также разделим на этапы:  
   5.2.1. Проверка наличия данных пользователя. Если пользователя нет, то процесс автоматически завершается:  
    ```
          if user_id not in users_data:
              logger.warning(f"User {user_id} is not in user_data")
              return
    ```  
   5.2.2. Проверка истечения времени на выполнение капчи. Если время истекло - удаляются все сообщения, связанные с капчей,
чтобы в чате было чисто:
```
           elapsed_time = time.time() - users_data[user_id]['start_time']
       if elapsed_time > 60:  # Прописываем условие, если время на выполнение капчи истекло
           await bot.delete_message(chat_id, message.message_id)
           await bot.delete_message(chat_id, users_data[user_id]['captcha_message_id'])
           await bot.send_message(chat_id, "Время на выполнение капчи истекло. Попробуйте снова.")
           users_data.pop(user_id, None)
           return
```  
   5.2.3. Игнорирование пустого текста. Эта часть кода необходима для решения проблемы, когда пользователю отправляется
сообщение с капчей и он открывает клавиатуру, чтобы ему не засчитывалась автоматически одна неправильная попытка. В
случае, если сообщение, отправляемое пользователем равно `None` - мы возвращаемся к этой функции и не засчитываем ответ:
```
       if text is None:
        return
```
   5.2.4. Проверка правильности ответа. Поскольку наша задача получить правильный ответ, то я создал переменную `correct_result`,
которая будет сравниваться с записанным в словаре значением, которое было сгенерировано капчой 
`correct_result = users_data[user_id]['result']`  
Далее я провожу проверку на то, что полученный ответ является цифрой или соответствует/не соответствует правильному 
ответу: `if not text.isdigit() or int(text) != correct_result`  
В случае, если полученное от пользователя сообщение не прошло проверку - удаляем его ответ, чтобы не засорять чат: 
`await bot.delete_message(chat_id, message.message_id)`    
Также здесь мы засчитываем неправильные ответы и обновляем значение в словаре и фиксируем оставшееся время:
```
           correct_result = users_data[user_id]['result']
        if not text.isdigit() or int(
                text) != correct_result:  # Проверка на неправильный ответ (не цифры или неправильный ответ)
            await bot.delete_message(chat_id, message.message_id)
            users_data[user_id]['attempts'] += 1
            remaining_attempts = 3 - users_data[user_id]['attempts']
            remaining_time = 60 - elapsed_time
```
   5.2.5. Обработка превышения количества попыток. Если пользователем введено более 3-х неправильных ответов, то он
исключается из чата посредством бана, это реализовано в функции `bot.ban.chat_member(chat_id, user_id)`. Далее система
уведомляет об этом всех пользователей `await bot.send_message(chat_id, f"{first_name} не прошел(а) проверку. 
Она вернется?")` и записывает соответствующую информацию в логах `logger.info(f"Пользователь {first_name} был исключен 
из чата по причине отсутствия правильного ответа")`. Но чтобы пользователь имел возможность вернуться и войти в чат,
система сразу после исключения снимает бан `bot.unban_chat_member(chat_id, user_id)`:
   ```
           if users_data[user_id]['attempts'] >= 3:
            try:
                await bot.ban_chat_member(chat_id, user_id)  # Исключаем пользователя посредством бана
                first_name = users_data[user_id]['first_name']
                await bot.send_message(chat_id, f"{first_name} не прошел(а) проверку. Она вернется?")
                users_data.pop(user_id, None)
                logger.info(f"Пользователь {first_name} был исключен из чата по причине отсутствия правильного ответа")
                await bot.unban_chat_member(chat_id, user_id)  # Немедленное снятие бана, потому что нужно давать второй шанс
   ```
   Если пользователь (админ), каким-либо образом попадает на проверку капчи (естественным или через функцию `test_captcha`)
, то предусмотрен блок, который не позволит удалить админа:
   ```
               except Exception as e:
                if "can't remove chat owner" in str(e):
                    if 'warning_message_id' in users_data[user_id]:
                        await bot.delete_message(chat_id, users_data[user_id]['warning_message_id'])
                    keyboard = InlineKeyboardMarkup(inline_keyboard=[
                        [InlineKeyboardButton(text="🪄 Волшебная палочка", callback_data='admin_warning')]
                    ])
                    sent_message = await bot.send_message(chat_id, "Кот, ну нельзя удалять админа",
                                                          reply_markup=keyboard)
                    users_data[user_id]['warning_message_id'] = sent_message.message_id
                    logger.info(f"Пользователь {user_id} попытался удалить админа в чате {chat_id}")
   ```
5.2.6. Обработка неправильного ответа.   
Основным тригером является проверка на некорректное сообщение отправленное пользователем
`if 'warning_message_id' in users_data[user_id]:`.   
В случае, если система определеяет ответ пользователя как неправильный, то она удаляет такое сообщение:
`await bot.delete_message(chat_id, users_data[user_id]['warning_message_id'])`, затем из данных удаляется такое сообщение.
Попытка не снимается, т.к. она была снята вначале функции.  
Взамен пользователь получает информационное сообщение с
текущим количеством попыток и оставшимся временем для решения уравнения `warning_message = await bot.send_message(chat_id,
f"Ответ неправильный, попробуй еще.Осталось {remaining_attempts} попыток.\n\n Оставшееся время: {int(remaining_time)} 
секунд")`  
После чего система фиксирует id такого информационного сообщения: `users_data[user_id]['warning_message_id'] = 
warning_message.message_id` и возвращает пользователя, если у него остались попытки к вводу нового ответа через `return`:
```
           else:
            if 'warning_message_id' in users_data[user_id]:
                await bot.delete_message(chat_id, users_data[user_id]['warning_message_id'])
                users_data[user_id].pop('warning_message_id', None)  # Удаляем предупреждающее сообщение из данных

            warning_message = await bot.send_message(chat_id,
                                                     f"Ответ неправильный, попробуй еще. "
                                                     f"Осталось {remaining_attempts} попыток.\n\n"
                                                     f"Оставшееся время: {int(remaining_time)} секунд")
            users_data[user_id]['warning_message_id'] = warning_message.message_id
        return
   ```
   5.2.7. Обработка правильного ответа.  
В случае ввода пользователем правильного ответа в пределах отведенного времени, то система удаляет сообщение с ответом
и капчей:
   ```
       await bot.delete_message(chat_id, message.message_id)
    await bot.delete_message(chat_id, users_data[user_id]['captcha_message_id'])
    if 'warning_message_id' in users_data[user_id]:
        await bot.delete_message(chat_id, users_data[user_id]['warning_message_id'])
   ```
   Затем мы определяем `first_name` для того, чтобы получить возможность вызвать `join_message()`, в котором обратимся к
пользователю по имени.  
Удаляем пользователя из списка пользователей, которые подлежат проверке, для того, чтобы отправить ему поздравительное
сообщение, т.к. критерием успеха в `join_message` у нас указана проверка `if user_id not in users_data:`. Удаление
происходит в 
`users_data.pop(user_id, None)`.  
Затем локально импортируем функцию `join_message`, т.к. в противном случае рискуем попасть на цикличный импорт `from 
botlogic.views import join_message`  
И делаем запись в логах, о том, что пользовал дал правильный ответ: `logger.info(f"Пользователь {user_id} дал 
правильный ответ")`: 
   ```
    first_name = users_data[user_id]['first_name']
    users_data.pop(user_id, None)
    from botlogic.views import join_message
    await join_message(bot, chat_id, user_id, first_name)
    logger.info(f"Пользователь {user_id} дал правильный ответ")
   ```

6. Функция `handle_message` нам нужна для того, чтобы улавливать сообщения, которые мы получаем от пользователя и
передавать ответы в `check_user_captcha`, без этого аргумент `message` в вышеуказанной функции не будет работать.
Также без аргумента `message` мы получаем ошибки о множественном вызове `check_user_captcha`: 
`TypeError: check_user_captcha() got multiple values for argument 'bot'`  
Поэтому тут все просто:  
6.1. В качестве аргмуента для этой фунукции используем: `message: types.Message`
6.2. Определяем `chat_id` - группу в которой пользователь проходит проверку, `user_id` - пользователя, который отправил
сообщение и `text` - сообщение, которое дал пользователь. 
Затем проводим проверку, что этот пользователь у нас отмечен, как пользователь, который проходит проверку для обработки
в функции `check_user_captcha()`: ` if user_id in users_data:`.   
Если пользователь находится в этом списке, то вызываем функцию `check_user_captcha()` и передаем в нее `text`

   ```
   async def handle_message(message: types.Message):
       chat_id = message.chat.id
       user_id = message.from_user.id
       text = message.text
   
       if user_id in users_data:
           await check_user_captcha(message.bot, chat_id, user_id, text, message)

   ```

7. Функция `test_captcha()` принимает аргументы `message: types.Message` - для обработки сообщения, которое инициирует
тест, `bot` - для императивного тона боту (чтобы заставить его делать в порядке исключения).  
    В рамках этой функции мы добавляем имитацию добавления нового пользователя, чтобы пройти отладку без сторонних 
учетных записей. Для этого мы определяем, кто такой "новый", а кто такой "старый" пользователь в `new_member` и 
`old_member` соответственно.

    - `new_member` — объект `ChatMemberMember`, представляющий нового участника чата.
        - `status='member'` указывает, что пользователь является участником.
        - `user=message.from_user` указывает, что пользователь берется из отправителя сообщения.
        - `until_date=None` означает, что членство не ограничено по времени.
        - `is_member=True` подтверждает, что пользователь является участником.
    - `old_member` — объект `ChatMemberLeft`, представляющий состояние пользователя до входа в чат.
        - `status='left'` указывает, что пользователь покинул чат.
        - `user=message.from_user` указывает на того же пользователя.
        - `until_date=None` означает, что дата выхода не указана.

    Затем мы определяем, что такое `event`. На самом деле определение этой функции было необходимо, поскольку эта 
категория была крепко и глубоко имплементирована в существующий код бота, на основе которого строилось задание.
    - `event` — объект `ChatMemberUpdated`, представляющий событие обновления состояния участника чата.
        - `chat=message.chat` указывает на чат, в котором происходит событие.
        - `from_user=message.from_user` указывает на пользователя, инициировавшего событие.
        - `date=message.date` указывает дату события.
        - `old_chat_member=old_member` — прежнее состояние участника чата.
        - `new_chat_member=new_member` — новое состояние участника чата.
Мы также использовали локальный импорт функции `on_user_join()`, чтобы не наткнуться на цикличный импорт. После того, как 
мы все определили и импортировали - переходим непосредственно к вызову `on_user_join()` и передаем в него определенные
ранее переменные `event` и `bot` 

    ```
   async def test_captcha(message: types.Message, bot):
      # Добавляем имитацию добавления нового пользователя, чтобы пройти отладку без сторонних учеток
      new_member = ChatMemberMember(status='member', user=message.from_user, until_date=None, is_member=True)
      old_member = ChatMemberLeft(status='left', user=message.from_user, until_date=None)
      event = ChatMemberUpdated(chat=message.chat, from_user=message.from_user, date=message.date,
                                 old_chat_member=old_member, new_chat_member=new_member)

      from botlogic.handlers.events import on_user_join 
      await on_user_join(event, bot)
   ```

8. Последняя функция из файла `check_captcha.py` это `delete_admin_warning_callback()`. В ней мы просто проводим ряд
проверок, для того, чтобы "вошлебная палочка" из `test_captcha` работала на ура:
async def delete_admin_warning_callback(call: CallbackQuery):
    user_id = call.from_user.id
    chat_id = call.message.chat.id

    if user_id in users_data:
        data = users_data[user_id]

        # Попробуем удалить сообщения, если они существуют. Но удалить сообщение с /test_captcha
        # все равно никак не выходит, а играться с message_id впадлу

        if 'captcha_message_id' in data:
            try:
                await call.bot.delete_message(chat_id, data['captcha_message_id'])
            except Exception as e:
                logger.warning(f"Ошибка при удалении сообщения с капчей: {e}")

        if 'warning_message_id' in data:
            try:
                await call.bot.delete_message(chat_id, data['warning_message_id'])
            except Exception as e:
                logger.warning(f"Ошибка при удалении предупреждающего сообщения: {e}")

        if 'test_captcha_message_id' in data:
            try:
                await call.bot.delete_message(chat_id, data['test_captcha_message_id'])
            except Exception as e:
                logger.warning(f"Ошибка при удалении сообщения пользователя с командой: {e}")

        # Удаляем сообщение с волшебной палочкой
        try:
            await call.bot.delete_message(chat_id, call.message.message_id)
        except Exception as e:
            logger.warning(f"Ошибка при удалении сообщения с волшебной палочкой: {e}")

        # Удаляем данные пользователя
        users_data.pop(user_id, None)

        await call.answer("Сообщения удалены и данные очищены")
9. Как говорилось ранее, были изменены аргументы для вызова функции `join_message()` в `views.py`, а именно добавлены:
`bot`, `chat_id`, `user_id`. Данная функция теперь должна вызываться следующим образом: 
`await join_message(bot, chat_id, user_id, first_name)`  
Также, была добавлена проверка, новый ли пользователь перед тем как отправить ему поздравительное сообщение с прохождением
капчи: `if user_id not in users_data:`.   
Вместо `return` я поставил `await bot.send_message()`, потому что в обратном случае невозможно было провести проверку.

   Полный обновленный код этой функции выглядит теперь так:
   ```
   async def join_message(bot, chat_id, user_id, first_name):
    if user_id not in users_data:
        await bot.send_message(chat_id,f"""Добро пожаловать в нашу группу, {first_name}!

   Давай знакомиться. 

   Расскажи немного о себе, своих увлечениях и о своём пути в программировании.""")
      ```
10. Также были внесены изменения в файл `events.py` в части `on_user_join()` и `on_user_left()`  
    10.1.1. Для вызова `on_user_join` добавлен аргумент 'bot'  
    10.1.2. Теперь при вступлении нового пользователя в группу сразу запускается функция `send_captcha()`  
    
        async def on_user_join(event: types.ChatMemberUpdated, bot):
            await send_captcha(bot, event.chat.id, event.from_user.id, event.from_user.first_name)
    
    10.2.1. В функции `on_user_left()` добавлен вызов функции `await sleep(5)`, для того чтобы корректно удалялись сообщения при бане пользователя.

        async def on_user_left(event: ChatMemberUpdated) -> None:
            if event.chat.id == secrets.group_id:
                await sleep(5)
                await event.answer(views.left_message(event.old_chat_member.user.first_name))

11. Напоследок, поскольку в данном коде не подразумевается использование диспетчера или роутеров, то необходимо было
зарегестрировать все обработчики в `main.py`  
    11.1. Сперва импорты
    ```
    from botlogic.utils.check_captcha import check_user_captcha, delete_admin_warning_callback, check_captcha_timeouts, \
    handle_message, test_captcha
    ```
    11.2. Затем регистрируем все, соблюдая последовательность и используя magic фильтры, где это возможно:
    ```
    dp.message.register(test_captcha, Command(commands=['test_captcha']))
    dp.message.register(handle_message)
    dp.message.register(check_user_captcha)
    dp.message.register(check_captcha_timeouts)
    dp.chat_member.register(on_user_join, ChatMemberUpdatedFilter(IS_NOT_MEMBER >> IS_MEMBER))
    dp.callback_query.register(delete_admin_warning_callback, F.data == "admin_warning")
    ```
    11.3. Итоговый, обновленный код `main.py` выглядит так: 
     ```
     import asyncio

    from aiogram import Dispatcher, F
    from aiogram.filters import Command, ChatMemberUpdatedFilter, IS_NOT_MEMBER, IS_MEMBER

    from botlogic.handlers import send_file, simple, weather_fsm, payment
    from botlogic.handlers.events import start_bot, stop_bot, on_user_join, on_user_left
    from botlogic.handlers.filter_words import check_message
    from botlogic.settings import bot
    from botlogic.utils.statesform import SendFileSteps, GetWeatherSteps
    from botlogic.utils.check_captcha import check_user_captcha, delete_admin_warning_callback, check_captcha_timeouts, \
    handle_message, test_captcha


    async def start():
           dp = Dispatcher()

           dp.startup.register(start_bot)
           dp.shutdown.register(stop_bot)

           dp.pre_checkout_query.register(payment.pre_checkout_handler)

           dp.message.register(simple.start_command, Command(commands="start"))
           dp.message.register(simple.about_command, Command(commands="about"))
           dp.message.register(simple.help_command, Command(commands="help"))
           dp.message.register(send_file.send_file_start, Command(commands="get_file"))
           dp.message.register(send_file.send_file_get_data, SendFileSteps.get_code_from_user)

           dp.message.register(payment.pay_support_handler, Command(commands="paysupport"))
           dp.message.register(payment.send_invoice_handler, Command(commands="donate"))
           dp.message.register(payment.success_payment_handler, F.successful_payment)

           dp.message.register(weather_fsm.get_weather_command, Command(commands="weather"))
           dp.message.register(weather_fsm.get_by_city, GetWeatherSteps.BY_CITY)
           dp.message.register(test_captcha, Command(commands=['test_captcha']))
           dp.message.register(handle_message)
           dp.message.register(check_user_captcha)
           dp.message.register(check_captcha_timeouts)
           dp.chat_member.register(on_user_join, ChatMemberUpdatedFilter(IS_NOT_MEMBER >> IS_MEMBER))
           dp.callback_query.register(delete_admin_warning_callback, F.data == "admin_warning")
           dp.message.register(check_message)
           dp.chat_member.register(on_user_left, ChatMemberUpdatedFilter(IS_MEMBER >> IS_NOT_MEMBER)
           )

        try:
            await dp.start_polling(bot)
        finally:
            await bot.session.close()


    if __name__ == "__main__":
        asyncio.run(start())

     ```

## Как участвовать?
1. Необходимо сделать fork (именно fork, а не clone!) проекта. 
2. Написать функционал антиспама в отдельной ветке.
3. Убедиться, что всё работает.
4. Сделать push в свой репозиторий и из него pull request в наш.
5. Ждать начала голосования и участвовать в обсуждении своего и решений других участников.

## Используемые библиотеки
- aiogram 3
- pydantic-settings
- requests

## Запуск
1. Создать и активировать виртуальное окружение:
   ```bash
   python -m venv .venv

   # для Windows
   venv\Scripts\activate.ps1
   # или 
   venv\Scripts\activate.bat

   # для *NIX-систем
   source venv/bin/activate
   ```
2. Установить зависимости:
   ```bash
   pip install -r requirements.txt
   ```
3. Переименовать `.env.example` в `.env` и вписать соответствующие данные:
   ```
   TOKEN=ваш_токен_бота
   ADMIN_ID=id_администратора
   GROUP_ID=id_группы
   WEATHER_KEY=токен_погоды  # не обязателен для конкурса
   AUDIO_KEY_ID=id_распознавания_голоса  # не обязателен для конкурса
   AUDIO_KEY_SECRET=токен_распознавания_голоса  # не обязателен для конкурса
   ```
4. Запустить бота:
   ```bash
   python main.py
   ```
   
## Автор
Иван Ашихмин  
Telegram-канал "[Код на салфетке](https://t.me/press_any_button)"]()