#Описание API

###API для поставщика

```
Изменение статуса магазина

POST http://localhost:8000/change_shop_status/
Authorization: Token 0c1b2af70d2bd1455de0204c9b7521e6773ef15a

{
    "status": "Status of shop has ben changed"
}

200 OK

При отправке запроса изменяется сатус активности магазина, 
к которому относится данный пользователь. Если же пользователь
не является работником какого-либо магазина возникает ошибка.

403 FORBIDDEN

{
    "status": "You are not staff"
}

```

```
Получение заказанных продуктов

GET http://localhost:8000/get_orders/
Authorization: Token 0c1b2af70d2bd1455de0204c9b7521e6773ef15a

200 OK 

{
  "2": [
    {
      "orderitem_id": 5,
      "orderitem_state": "confirmed",
      "product_name": "Смартфон Apple iPhone XR 256GB (красный)",
      "quantity": 3
    }
  ]
}

При отправке запроса возвращает объект типа ключ-значения, где 
ключ - номер заказа, к которому относится данный пункт заказа,
а значение - список, состоящий из основной информации о пунктax 
соответствующего заказа. Если же пользователь не является работником
какого-либо магазина возникает ошибка.

403 FORBIDDEN

{
    "status": "You are not staff"
}

```

```
Публикация товаров

POST http://localhost:8000/product/
Authorization: Token 6a119f534d43f29078093a4c7d9d9d363b80de7a

200 OK

{
    "status": "OK"
}

При вызове функции считывает информацию из yaml файла определенного формата.
Запрос выполняется при условии, что пользователь является работником магазина,
указанного в yaml файле, иначе возникает ошибка.

```

### API для пользователя

```
Регистрация

POST http://localhost:8000/registration/
Content-Type: application/json

{
    "username" : "netology_dyplom2@mail.ru",
    "email": "netology_dyplom2@mail.ru",
    "password" : "12345678",
    "password2" : "12345678"
}

200 OK

При отправке регистриует пользователя, при условии, что данный email
не занят. Все поля показанные в примере обязательны. Автоматически 
отправляет сообщение на почту с подтверждающей email ссылкой. При этом
без подтверждения пользователь не сможет авторизоваться.

```

```
Авторизация

POST  http://localhost:8000/login/
Content-Type: application/json

{
    "username" : "netology_dyplom2@mail.ru",
    "password" : "12345678"
}

200 OK

{
  "token": "f8944b046fd2f2ce9a08b9ee37e802bcf844d102"
}

При отправке верного запроса авторизирует пользователя в системе,
возвращая при ответе его token. Все поля показанные в примере обязательны.
При неверном запросе возникает ошибка.

400 BAD REQUEST

{
    "status": "Bad request"
}

```

```
Выход из системы

POST http://localhost:8000/logout/
Content-Type: application/json
Authorization: Token f8944b046fd2f2ce9a08b9ee37e802bcf844d102

200 OK

{
  "status": "Logout has been completed"
}

При отправке запроса пользователь выходит из системы.

```

```
Получение всех продуктов

GET http://localhost:8000/product/
Authorization: Token 6a119f534d43f29078093a4c7d9d9d363b80de7a

200 OK

[
  {
    "id": 44,
    "name": "\u0421\u043c\u0430\u0440\u0442\u0444\u043e\u043d Apple iPhone XS Max 512GB (\u0437\u043e\u043b\u043e\u0442\u0438\u0441\u0442\u044b\u0439)"
  },
  {
    "id": 45,
    "name": "\u0421\u043c\u0430\u0440\u0442\u0444\u043e\u043d Apple iPhone XR 256GB (\u043a\u0440\u0430\u0441\u043d\u044b\u0439)"
  },
  {
    "id": 46,
    "name": "\u0421\u043c\u0430\u0440\u0442\u0444\u043e\u043d Apple iPhone XR 256GB (\u0447\u0435\u0440\u043d\u044b\u0439)"
  },
  {
    "id": 47,
    "name": "\u0421\u043c\u0430\u0440\u0442\u0444\u043e\u043d Apple iPhone XR 128GB (\u0441\u0438\u043d\u0438\u0439)"
  }
]

```

```
Получение информации о одном продукте

GET http://localhost:8000/prinf/47/

200 OK

{
  "id": 47,
  "name": "Смартфон Apple iPhone XR 128GB (синий)",
  "shop": "Связной",
  "model": "apple/iphone/xr",
  "price": 60000,
  "quantity": 7,
  "parameters": {
    "Диагональ (дюйм)": "6.1",
    "Разрешение (пикс)": "1792x828",
    "Встроенная память (Гб)": "256",
    "Цвет": "синий"
  }
}

При отпралении запроса возвращается информация о товаре под 
номером 47. Если отправляется запрос на несуществующий товар 
возникает ошибка. Авторизация при данном запросе не требуется.

404 Not Found

{
  "status": "This product is not found"
}

```

```
Заполнение контактной информации

POST http://localhost:8000/contact_info/
Content-Type: application/json
Authorization: Token 6a119f534d43f29078093a4c7d9d9d363b80de7a

{
    "adress": "hello",
    "t_number": "dfasdasd"
}

200 OK

{
  "status": "OK"
}

При вызове заполняет контактную иинформацию. Все поля указанные в примере
обязательны. Запрос работает только при отсутвующей контактной иноформации,
иначе возникает исключение.

200 OK

{
  "status": "Your contact details has been specified"
}

```

```
Просмотр своей контактной информации

GET http://localhost:8000/contact_info/
Content-Type: application/json
Authorization: Token 6a119f534d43f29078093a4c7d9d9d363b80de7a

200 OK

{
  "user_id": 45,
  "username": "netology_dyplom2@mail.ru",
  "adress": "hello",
  "telephone_number": "dfasdasd"
}

При запросе выдает личную контакную информацию.

```

```
Изменение своей контактной информации

PUT http://localhost:8000/contact_info/
Content-Type: application/json
Authorization: Token 0c1b2af70d2bd1455de0204c9b7521e6773ef15a

{
    "adress": "hel000000000",
    "t_number": "dfasdasd"
}

200 OK

{
  "status": "OK"
}

При запросе обновляет личную контактную информаци. Все поля показанные
в примере обязательны. Сработает только при существующей контакной
информации, иначе возникает исключение.

200 OK

{
    "status": "Your contact details are not specified"
}

```

```
Удаление контактной информации

DELETE http://localhost:8000/contact_info/
Authorization: Token 6a119f534d43f29078093a4c7d9d9d363b80de7a

200 OK

{
  "status": "OK"
}

При запросе удаляет личную информацию. Работает только при 
сущестующей контактной информации, иначе возникает исключение.

200 OK

{
    "status": "Your contact details are not specified"
}

```

```
Добавление товара в корзину

POST http://localhost:8000/basket/
Content-Type: application/json
Authorization: Token 6a119f534d43f29078093a4c7d9d9d363b80de7a

{
    "product_info": "45",
    "quantity": 3
}

200 OK

{
  "status": "OK"
}

При запросе добавляет товар в корзину. Все поля показанные в примере обязательны.
Сработает, если товар существует и существует заявленное количество товара, 
иначе возникает ошибка. В корзине могут быть только уникальные эелементы.

```

```
Получение товаров, находящихся в корзине

GET http://localhost:8000/basket/
Authorization: Token 0c1b2af70d2bd1455de0204c9b7521e6773ef15a

200 OK

{
  "1": {
    "id": 45,
    "name": "Смартфон Apple iPhone XR 256GB (красный)",
    "category": "Смартфоны",
    "shop": "Связной",
    "quantity": 3,
    "model": "apple/iphone/xr",
    "price": 65000
  }
}

При запросе возвращает объект типа ключ-значение, где ключ - порядковый 
номер товара в корзине, значение - основная информация о товаре.

```

```
Изменение количества заказанного товара

PATCH http://localhost:8000/basket/
Content-Type: application/json
Authorization: Token 6a119f534d43f29078093a4c7d9d9d363b80de7a

{
    "orderitem_id": "6",
    "quantity": 4
}

200 OK

{
  "status": "OK"
}

При запросе изменяет количество заказанного товара. Все поля показанные в 
примере обязательны. При указании неверного id пункта заказа или
количечества товара возникаю ошибки.

```

```
Очистка личной корзины

DELETE http://localhost:8000/basket/
Authorization: Token 6a119f534d43f29078093a4c7d9d9d363b80de7a

200 OK

{
  "status": "OK"
}

При запросе удаляет все товары из корзины.
```

```
Оформление заказа

POST http://localhost:8000/order/
Authorization: Token 6a119f534d43f29078093a4c7d9d9d363b80de7a

200 OK

{
  "status": "OK"
}

При запросе оформляет заказ, состоящий из заказов, находящихся в 
корзине. Если в корзине нет товаров возникает ошибка. После отправки
запроса на email пользователя приходит ссылка подтвержадющая заказ.
После подтверждения заказа всем пользователям, являющимися работниками
данного магазина, приходит email уведомление.

```

```
Получение истории всех заказов

GET http://localhost:8000/order/
Authorization: Token 6a119f534d43f29078093a4c7d9d9d363b80de7a

200 OK

{
  "1": {
    "order_id": 3,
    "order.state": "new"
  }
}

При запросе возвращает историю всех заказов в виде объекта
ключ-значение, где ключ - порядковый номер заказа в истории пользователя,
значение - основная информация о заказе.
```