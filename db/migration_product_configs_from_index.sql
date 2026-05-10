-- Полные description + config_json для эталонных SKU (синхрон с index.html PRODUCT_CONFIGS).
-- Выполнить в PostgreSQL один раз после seed. Ручное «Сохранить» в админке для каждой карточки не требуется.

BEGIN;

UPDATE products SET
  description = $d105$Сборка для 4К гейминга и стриминга на процессоре Intel 14-го поколения и видеокарте RTX 4080.

Абсолютно любые комплектующие ПК можно изменить по Вашим пожеланиям!

Характеристики:

• Процессор: Intel Core i7-14700K

• Оперативная память: DDR5 32GB 6000Mhz Kingston

• Видеокарта: NVIDIA RTX4080 16GB

• SSD: M2 NVME 2TB Kingston KC3000

• Блок питания: Phanteks AMP GH850W 80+ Gold

• Водяное охлаждение Thermalright 360мм

• Охлаждение: 6 ARGB вертушек

• Корпус: Lian Li 011 Dynamic RGB

⚙️ Полная настройка и сборка под ключ!

✔️ Windows, все необходимые драйвера, программы уже установлены!$d105$,
  config_json = $j105${"basePrice":259990,"baseCpu":"i7-14700K","baseGpu":"RTX4080","image":"photo/pc4_3.jpg","name":"AURUM 4K Streaming","description":"Сборка для 4К гейминга и стриминга на процессоре Intel 14-го поколения и видеокарте RTX 4080.\n\nАбсолютно любые комплектующие ПК можно изменить по Вашим пожеланиям!\n\nХарактеристики:\n\n• Процессор: Intel Core i7-14700K\n\n• Оперативная память: DDR5 32GB 6000Mhz Kingston\n\n• Видеокарта: NVIDIA RTX4080 16GB\n\n• SSD: M2 NVME 2TB Kingston KC3000\n\n• Блок питания: Phanteks AMP GH850W 80+ Gold\n\n• Водяное охлаждение Thermalright 360мм\n\n• Охлаждение: 6 ARGB вертушек\n\n• Корпус: Lian Li 011 Dynamic RGB\n\n⚙️ Полная настройка и сборка под ключ!\n\n✔️ Windows, все необходимые драйвера, программы уже установлены!","options":{"cpu":[{"name":"Intel Core i7-14700K","price":0,"selected":true},{"name":"AMD Ryzen 9 7900X","price":20000},{"name":"Intel Core i7-13700K","price":-10000},{"name":"AMD Ryzen 7 7800X3D","price":18000}],"gpu":[{"name":"NVIDIA RTX 4080 16GB","price":0,"selected":true},{"name":"NVIDIA RTX 4090 24GB","price":40000},{"name":"NVIDIA RTX 4070 TI SUPER 16GB","price":-15000},{"name":"AMD RX 7900 XTX 24GB","price":-10000}],"ssd":[{"name":"2TB NVMe SSD","price":0,"selected":true},{"name":"1TB NVMe SSD","price":-8000},{"name":"4TB NVMe SSD","price":15000},{"name":"2TB NVMe SSD + 4TB HDD","price":5000}],"warranty":[{"name":"1 год","price":0,"selected":true},{"name":"2 года","price":5000},{"name":"3 года","price":10000},{"name":"5 лет","price":20000}]}}$j105$::jsonb
WHERE id = 105;

UPDATE products SET
  description = $d103$Сбалансированная сборка для комфортного 4К гейминга.

Абсолютно любые комплектующие ПК можно изменить по Вашим пожеланиям!

Характеристики:

• Процессор: AMD Ryzen 9 7900X

• Оперативная память: DDR5 32GB 5600Mhz Kingston

• Видеокарта: NVIDIA RTX4070 12GB

• SSD: M2 NVME 1TB Kingston KC3000

• Блок питания: Phanteks AMP GH750W 80+ Gold

• Водяное охлаждение Thermalright 240мм

• Охлаждение: 4 ARGB вертушки

• Корпус: Lian Li Lancool 216 RGB

⚙️ Полная настройка и сборка под ключ!

✔️ Windows, все необходимые драйвера, программы уже установлены!$d103$,
  config_json = $j103${"basePrice":249990,"baseCpu":"R9 7900X","baseGpu":"RTX4070","image":"photo/pc4_4.jpg","name":"AURUM 4K Standard","description":"Сбалансированная сборка для комфортного 4К гейминга.\n\nАбсолютно любые комплектующие ПК можно изменить по Вашим пожеланиям!\n\nХарактеристики:\n\n• Процессор: AMD Ryzen 9 7900X\n\n• Оперативная память: DDR5 32GB 5600Mhz Kingston\n\n• Видеокарта: NVIDIA RTX4070 12GB\n\n• SSD: M2 NVME 1TB Kingston KC3000\n\n• Блок питания: Phanteks AMP GH750W 80+ Gold\n\n• Водяное охлаждение Thermalright 240мм\n\n• Охлаждение: 4 ARGB вертушки\n\n• Корпус: Lian Li Lancool 216 RGB\n\n⚙️ Полная настройка и сборка под ключ!\n\n✔️ Windows, все необходимые драйвера, программы уже установлены!","options":{"cpu":[{"name":"AMD Ryzen 9 7900X","price":0,"selected":true},{"name":"Intel Core i7-13700K","price":10000},{"name":"AMD Ryzen 9 7900X3D","price":20000},{"name":"Intel Core i5-13600K","price":-5000}],"gpu":[{"name":"NVIDIA RTX 4070 12GB","price":0,"selected":true},{"name":"NVIDIA RTX 4070 SUPER 12GB","price":10000},{"name":"NVIDIA RTX 4070 TI 12GB","price":15000},{"name":"NVIDIA RTX 4080 16GB","price":35000}],"ssd":[{"name":"1TB NVMe SSD","price":0,"selected":true},{"name":"2TB NVMe SSD","price":8000},{"name":"4TB NVMe SSD","price":23000},{"name":"1TB NVMe SSD + 2TB HDD","price":3000}],"warranty":[{"name":"1 год","price":0,"selected":true},{"name":"2 года","price":5000},{"name":"3 года","price":10000},{"name":"5 лет","price":20000}]}}$j103$::jsonb
WHERE id = 103;

UPDATE products SET
  description = $d104$Бюджетная сборка для входа в 4К гейминг.

Абсолютно любые комплектующие ПК можно изменить по Вашим пожеланиям!

Характеристики:

• Процессор: AMD Ryzen 7 7700X

• Оперативная память: DDR5 16GB 5600Mhz Kingston

• Видеокарта: NVIDIA RTX4070 12GB

• SSD: M2 NVME 1TB Kingston KC3000

• Блок питания: Phanteks AMP GH650W 80+ Bronze

• Воздушное охлаждение Thermalright Peerless Assassin

• Охлаждение: 3 ARGB вертушки

• Корпус: Lian Li Lancool 205 Mesh RGB

⚙️ Полная настройка и сборка под ключ!

✔️ Windows, все необходимые драйвера, программы уже установлены!$d104$,
  config_json = $j104${"basePrice":199990,"baseCpu":"R7 7700X","baseGpu":"RTX4070","image":"photo/pc4_4.jpg","name":"AURUM 4K Basic","description":"Бюджетная сборка для входа в 4К гейминг.\n\nАбсолютно любые комплектующие ПК можно изменить по Вашим пожеланиям!\n\nХарактеристики:\n\n• Процессор: AMD Ryzen 7 7700X\n\n• Оперативная память: DDR5 16GB 5600Mhz Kingston\n\n• Видеокарта: NVIDIA RTX4070 12GB\n\n• SSD: M2 NVME 1TB Kingston KC3000\n\n• Блок питания: Phanteks AMP GH650W 80+ Bronze\n\n• Воздушное охлаждение Thermalright Peerless Assassin\n\n• Охлаждение: 3 ARGB вертушки\n\n• Корпус: Lian Li Lancool 205 Mesh RGB\n\n⚙️ Полная настройка и сборка под ключ!\n\n✔️ Windows, все необходимые драйвера, программы уже установлены!","options":{"cpu":[{"name":"AMD Ryzen 7 7700X","price":0,"selected":true},{"name":"Intel Core i5-13600K","price":5000},{"name":"AMD Ryzen 7 7800X3D","price":15000},{"name":"Intel Core i7-13700K","price":20000}],"gpu":[{"name":"NVIDIA RTX 4070 12GB","price":0,"selected":true},{"name":"NVIDIA RTX 4070 TI 12GB","price":20000},{"name":"NVIDIA RTX 4060 TI 16GB","price":-10000},{"name":"AMD RX 7700 XT 12GB","price":-15000}],"ssd":[{"name":"1TB NVMe SSD","price":0,"selected":true},{"name":"2TB NVMe SSD","price":8000},{"name":"512GB NVMe SSD","price":-5000},{"name":"1TB NVMe SSD + 1TB HDD","price":2000}],"warranty":[{"name":"1 год","price":0,"selected":true},{"name":"2 года","price":5000},{"name":"3 года","price":10000},{"name":"5 лет","price":20000}]}}$j104$::jsonb
WHERE id = 104;

UPDATE products SET
  description = $d102$Мощная сборка для 4К гейминга с отличным соотношением цена/производительность.

Абсолютно любые комплектующие ПК можно изменить по Вашим пожеланиям!

Характеристики:

• Процессор: Intel Core i7-13700K

• Оперативная память: DDR5 32GB 6000Mhz Kingston

• Видеокарта: NVIDIA RTX4080 16GB

• SSD: M2 NVME 2TB Kingston KC3000

• Блок питания: Phanteks AMP GH850W 80+ Gold

• Водяное охлаждение Thermalright 360мм

• Охлаждение: 6 ARGB вертушек

• Корпус: Lian Li 011 Dynamic RGB

⚙️ Полная настройка и сборка под ключ!

✔️ Windows, все необходимые драйвера, программы уже установлены!$d102$,
  config_json = $j102${"basePrice":299990,"baseCpu":"i7-13700K","baseGpu":"RTX4080","image":"photo/pc4_2.jpg","name":"AURUM 4K Elite","description":"Мощная сборка для 4К гейминга с отличным соотношением цена/производительность.\n\nАбсолютно любые комплектующие ПК можно изменить по Вашим пожеланиям!\n\nХарактеристики:\n\n• Процессор: Intel Core i7-13700K\n\n• Оперативная память: DDR5 32GB 6000Mhz Kingston\n\n• Видеокарта: NVIDIA RTX4080 16GB\n\n• SSD: M2 NVME 2TB Kingston KC3000\n\n• Блок питания: Phanteks AMP GH850W 80+ Gold\n\n• Водяное охлаждение Thermalright 360мм\n\n• Охлаждение: 6 ARGB вертушек\n\n• Корпус: Lian Li 011 Dynamic RGB\n\n⚙️ Полная настройка и сборка под ключ!\n\n✔️ Windows, все необходимые драйвера, программы уже установлены!","options":{"cpu":[{"name":"Intel Core i7-13700K","price":0,"selected":true},{"name":"AMD Ryzen 9 7900X","price":20000},{"name":"Intel Core i7-14700K","price":15000},{"name":"AMD Ryzen 7 7800X3D","price":18000}],"gpu":[{"name":"NVIDIA RTX 4080 16GB","price":0,"selected":true},{"name":"NVIDIA RTX 4090 24GB","price":40000},{"name":"NVIDIA RTX 4070 TI SUPER 16GB","price":-15000},{"name":"AMD RX 7900 XTX 24GB","price":-10000}],"ssd":[{"name":"2TB NVMe SSD","price":0,"selected":true},{"name":"1TB NVMe SSD","price":-8000},{"name":"4TB NVMe SSD","price":15000},{"name":"2TB NVMe SSD + 4TB HDD","price":5000}],"warranty":[{"name":"1 год","price":0,"selected":true},{"name":"2 года","price":5000},{"name":"3 года","price":10000},{"name":"5 лет","price":20000}]}}$j102$::jsonb
WHERE id = 102;

UPDATE products SET
  description = $d101$Самый мощный вариант для 4К гейминга на современном процессоре Ryzen с видеокартой Nvidia 5000 серии.

Абсолютно любые комплектующие ПК можно изменить по Вашим пожеланиям!

Характеристики:

• Процессор: AMD Ryzen 9 9950x3d

• Оперативная память: DDR5 64GB 6000Mhz Kingston

• Видеокарта: NVIDIA RTX5090 32GB Gamerock

• SSD: M2 NVME 2TB Kingston KC3000

• Блок питания: Phanteks AMP GH1000W 80+ Platinum

• Водяное охлаждение Thermalright 360мм с LCD дисплеем

• Охлаждение: 9 ARGB вертушек + пульт

• Корпус: Lian Li 011 Dynamic EVO RGB

⚙️ Полная настройка и сборка под ключ!

✔️ Windows, все необходимые драйвера, программы уже установлены!$d101$,
  config_json = $j101${"basePrice":349990,"baseCpu":"i9-13900K","baseGpu":"RTX4090","image":"photo/pc4_1.jpg","name":"AURUM 4K Pro","description":"Самый мощный вариант для 4К гейминга на современном процессоре Ryzen с видеокартой Nvidia 5000 серии.\n\nАбсолютно любые комплектующие ПК можно изменить по Вашим пожеланиям!\n\nХарактеристики:\n\n• Процессор: AMD Ryzen 9 9950x3d\n\n• Оперативная память: DDR5 64GB 6000Mhz Kingston\n\n• Видеокарта: NVIDIA RTX5090 32GB Gamerock\n\n• SSD: M2 NVME 2TB Kingston KC3000\n\n• Блок питания: Phanteks AMP GH1000W 80+ Platinum\n\n• Водяное охлаждение Thermalright 360мм с LCD дисплеем\n\n• Охлаждение: 9 ARGB вертушек + пульт\n\n• Корпус: Lian Li 011 Dynamic EVO RGB\n\n⚙️ Полная настройка и сборка под ключ!\n\n✔️ Windows, все необходимые драйвера, программы уже установлены!","options":{"cpu":[{"name":"Intel Core i9-13900K","price":0,"selected":true},{"name":"AMD Ryzen 9 9950X3D","price":25000},{"name":"Intel Core i9-14900K","price":15000},{"name":"AMD Ryzen 9 7950X3D","price":20000}],"gpu":[{"name":"NVIDIA RTX 4090 24GB","price":0,"selected":true},{"name":"NVIDIA RTX 5090 32GB","price":50000},{"name":"NVIDIA RTX 4080 SUPER 16GB","price":-20000},{"name":"AMD RX 7900 XTX 24GB","price":-15000}],"ssd":[{"name":"2TB NVMe SSD","price":0,"selected":true},{"name":"1TB NVMe SSD","price":-8000},{"name":"4TB NVMe SSD","price":15000},{"name":"2TB NVMe SSD + 4TB HDD","price":5000}],"warranty":[{"name":"1 год","price":0,"selected":true},{"name":"2 года","price":5000},{"name":"3 года","price":10000},{"name":"5 лет","price":20000}]}}$j101$::jsonb
WHERE id = 101;

UPDATE products SET
  description = $d204$Бюджетная сборка для входа в 2К гейминг.

Абсолютно любые комплектующие ПК можно изменить по Вашим пожеланиям!

Характеристики:

• Процессор: AMD Ryzen 5 7600

• Оперативная память: DDR5 16GB 5600Mhz Kingston

• Видеокарта: NVIDIA RTX4060 8GB

• SSD: M2 NVME 1TB Kingston KC3000

• Блок питания: Phanteks AMP GH600W 80+ Bronze

• Воздушное охлаждение Thermalright Assassin X

• Охлаждение: 2 ARGB вертушки

• Корпус: Lian Li Lancool 205 Mesh

⚙️ Полная настройка и сборка под ключ!

✔️ Windows, все необходимые драйвера, программы уже установлены!$d204$,
  config_json = $j204${"basePrice":149990,"baseCpu":"R5 7600","baseGpu":"RTX4060","image":"photo/pc2_4.jpg","name":"AURUM 2K Starter","description":"Бюджетная сборка для входа в 2К гейминг.\n\nАбсолютно любые комплектующие ПК можно изменить по Вашим пожеланиям!\n\nХарактеристики:\n\n• Процессор: AMD Ryzen 5 7600\n\n• Оперативная память: DDR5 16GB 5600Mhz Kingston\n\n• Видеокарта: NVIDIA RTX4060 8GB\n\n• SSD: M2 NVME 1TB Kingston KC3000\n\n• Блок питания: Phanteks AMP GH600W 80+ Bronze\n\n• Воздушное охлаждение Thermalright Assassin X\n\n• Охлаждение: 2 ARGB вертушки\n\n• Корпус: Lian Li Lancool 205 Mesh\n\n⚙️ Полная настройка и сборка под ключ!\n\n✔️ Windows, все необходимые драйвера, программы уже установлены!","options":{"cpu":[{"name":"AMD Ryzen 5 7600","price":0,"selected":true},{"name":"Intel Core i5-13400F","price":5000},{"name":"AMD Ryzen 7 7700X","price":15000},{"name":"Intel Core i5-13600KF","price":20000}],"gpu":[{"name":"NVIDIA RTX 4060 8GB","price":0,"selected":true},{"name":"NVIDIA RTX 4060 Ti 16GB","price":15000},{"name":"NVIDIA RTX 4070 SUPER 12GB","price":25000},{"name":"AMD RX 7600 8GB","price":-15000}],"ssd":[{"name":"1TB NVMe SSD","price":0,"selected":true},{"name":"2TB NVMe SSD","price":8000},{"name":"512GB NVMe SSD","price":-5000},{"name":"1TB NVMe SSD + 1TB HDD","price":2000}],"warranty":[{"name":"1 год","price":0,"selected":true},{"name":"2 года","price":5000},{"name":"3 года","price":10000},{"name":"5 лет","price":20000}]}}$j204$::jsonb
WHERE id = 204;

UPDATE products SET
  description = $d202$Отличная сборка для 2К гейминга с процессором X3D.

Абсолютно любые комплектующие ПК можно изменить по Вашим пожеланиям!

Характеристики:

• Процессор: AMD Ryzen 7 7800X3D

• Оперативная память: DDR5 32GB 6000Mhz Kingston

• Видеокарта: NVIDIA RTX4070 12GB

• SSD: M2 NVME 2TB Kingston KC3000

• Блок питания: Phanteks AMP GH750W 80+ Gold

• Водяное охлаждение Thermalright 240мм

• Охлаждение: 4 ARGB вертушки

• Корпус: Lian Li Lancool 216 RGB

⚙️ Полная настройка и сборка под ключ!

✔️ Windows, все необходимые драйвера, программы уже установлены!$d202$,
  config_json = $j202${"basePrice":199990,"baseCpu":"R7 7800X3D","baseGpu":"RTX4070","image":"photo/pc2_2.jpg","name":"AURUM 2K Pro","description":"Отличная сборка для 2К гейминга с процессором X3D.\n\nАбсолютно любые комплектующие ПК можно изменить по Вашим пожеланиям!\n\nХарактеристики:\n\n• Процессор: AMD Ryzen 7 7800X3D\n\n• Оперативная память: DDR5 32GB 6000Mhz Kingston\n\n• Видеокарта: NVIDIA RTX4070 12GB\n\n• SSD: M2 NVME 2TB Kingston KC3000\n\n• Блок питания: Phanteks AMP GH750W 80+ Gold\n\n• Водяное охлаждение Thermalright 240мм\n\n• Охлаждение: 4 ARGB вертушки\n\n• Корпус: Lian Li Lancool 216 RGB\n\n⚙️ Полная настройка и сборка под ключ!\n\n✔️ Windows, все необходимые драйвера, программы уже установлены!","options":{"cpu":[{"name":"AMD Ryzen 7 7800X3D","price":0,"selected":true},{"name":"Intel Core i7-13700K","price":10000},{"name":"AMD Ryzen 9 7900X","price":15000},{"name":"Intel Core i5-13600K","price":-5000}],"gpu":[{"name":"NVIDIA RTX 4070 12GB","price":0,"selected":true},{"name":"NVIDIA RTX 4070 SUPER 12GB","price":10000},{"name":"NVIDIA RTX 4070 TI SUPER 16GB","price":20000},{"name":"NVIDIA RTX 4080 SUPER 16GB","price":35000}],"ssd":[{"name":"2TB NVMe SSD","price":0,"selected":true},{"name":"1TB NVMe SSD","price":-8000},{"name":"4TB NVMe SSD","price":15000},{"name":"2TB NVMe SSD + 2TB HDD","price":3000}],"warranty":[{"name":"1 год","price":0,"selected":true},{"name":"2 года","price":5000},{"name":"3 года","price":10000},{"name":"5 лет","price":20000}]}}$j202$::jsonb
WHERE id = 202;

UPDATE products SET
  description = $d201$Топовая сборка для 2К гейминга с максимальной производительностью.

Абсолютно любые комплектующие ПК можно изменить по Вашим пожеланиям!

Характеристики:

• Процессор: Intel Core i7-13700KF

• Оперативная память: DDR5 32GB 6000Mhz Kingston

• Видеокарта: NVIDIA RTX4080 16GB

• SSD: M2 NVME 2TB Kingston KC3000

• Блок питания: Phanteks AMP GH850W 80+ Gold

• Водяное охлаждение Thermalright 360мм

• Охлаждение: 6 ARGB вертушек

• Корпус: Lian Li 011 Dynamic RGB

⚙️ Полная настройка и сборка под ключ!

✔️ Windows, все необходимые драйвера, программы уже установлены!$d201$,
  config_json = $j201${"basePrice":239990,"baseCpu":"i7-13700KF","baseGpu":"RTX4080","image":"photo/pc2_1.jpg","name":"AURUM 2K Ultra","description":"Топовая сборка для 2К гейминга с максимальной производительностью.\n\nАбсолютно любые комплектующие ПК можно изменить по Вашим пожеланиям!\n\nХарактеристики:\n\n• Процессор: Intel Core i7-13700KF\n\n• Оперативная память: DDR5 32GB 6000Mhz Kingston\n\n• Видеокарта: NVIDIA RTX4080 16GB\n\n• SSD: M2 NVME 2TB Kingston KC3000\n\n• Блок питания: Phanteks AMP GH850W 80+ Gold\n\n• Водяное охлаждение Thermalright 360мм\n\n• Охлаждение: 6 ARGB вертушек\n\n• Корпус: Lian Li 011 Dynamic RGB\n\n⚙️ Полная настройка и сборка под ключ!\n\n✔️ Windows, все необходимые драйвера, программы уже установлены!","options":{"cpu":[{"name":"Intel Core i7-13700KF","price":0,"selected":true},{"name":"AMD Ryzen 7 7800X3D","price":15000},{"name":"Intel Core i7-14700KF","price":10000},{"name":"AMD Ryzen 9 7900X","price":20000}],"gpu":[{"name":"NVIDIA RTX 4080 16GB","price":0,"selected":true},{"name":"NVIDIA RTX 4080 SUPER 16GB","price":12000},{"name":"NVIDIA RTX 4090 24GB","price":35000},{"name":"NVIDIA RTX 4070 TI SUPER 16GB","price":-15000}],"ssd":[{"name":"2TB NVMe SSD","price":0,"selected":true},{"name":"1TB NVMe SSD","price":-8000},{"name":"4TB NVMe SSD","price":15000},{"name":"2TB NVMe SSD + 4TB HDD","price":5000}],"warranty":[{"name":"1 год","price":0,"selected":true},{"name":"2 года","price":5000},{"name":"3 года","price":10000},{"name":"5 лет","price":20000}]}}$j201$::jsonb
WHERE id = 201;

UPDATE products SET
  description = $d203$Сбалансированная сборка для комфортного 2К гейминга.

Абсолютно любые комплектующие ПК можно изменить по Вашим пожеланиям!

Характеристики:

• Процессор: Intel Core i5-13600KF

• Оперативная память: DDR5 16GB 5600Mhz Kingston

• Видеокарта: NVIDIA RTX4070 12GB

• SSD: M2 NVME 1TB Kingston KC3000

• Блок питания: Phanteks AMP GH650W 80+ Bronze

• Воздушное охлаждение Thermalright Peerless Assassin

• Охлаждение: 3 ARGB вертушки

• Корпус: Lian Li Lancool 205 Mesh RGB

⚙️ Полная настройка и сборка под ключ!

✔️ Windows, все необходимые драйвера, программы уже установлены!$d203$,
  config_json = $j203${"basePrice":169990,"baseCpu":"i5-13600KF","baseGpu":"RTX4070","image":"photo/pc2_3.jpg","name":"AURUM 2K Core","description":"Сбалансированная сборка для комфортного 2К гейминга.\n\nАбсолютно любые комплектующие ПК можно изменить по Вашим пожеланиям!\n\nХарактеристики:\n\n• Процессор: Intel Core i5-13600KF\n\n• Оперативная память: DDR5 16GB 5600Mhz Kingston\n\n• Видеокарта: NVIDIA RTX4070 12GB\n\n• SSD: M2 NVME 1TB Kingston KC3000\n\n• Блок питания: Phanteks AMP GH650W 80+ Bronze\n\n• Воздушное охлаждение Thermalright Peerless Assassin\n\n• Охлаждение: 3 ARGB вертушки\n\n• Корпус: Lian Li Lancool 205 Mesh RGB\n\n⚙️ Полная настройка и сборка под ключ!\n\n✔️ Windows, все необходимые драйвера, программы уже установлены!","options":{"cpu":[{"name":"Intel Core i5-13600KF","price":0,"selected":true},{"name":"AMD Ryzen 7 7700X","price":10000},{"name":"Intel Core i7-13700KF","price":20000},{"name":"AMD Ryzen 5 7600","price":-5000}],"gpu":[{"name":"NVIDIA RTX 4070 12GB","price":0,"selected":true},{"name":"NVIDIA RTX 4070 SUPER 12GB","price":10000},{"name":"NVIDIA RTX 4070 TI SUPER 16GB","price":20000},{"name":"NVIDIA RTX 4060 TI 16GB","price":-12000}],"ssd":[{"name":"1TB NVMe SSD","price":0,"selected":true},{"name":"2TB NVMe SSD","price":8000},{"name":"512GB NVMe SSD","price":-5000},{"name":"1TB NVMe SSD + 1TB HDD","price":2000}],"warranty":[{"name":"1 год","price":0,"selected":true},{"name":"2 года","price":5000},{"name":"3 года","price":10000},{"name":"5 лет","price":20000}]}}$j203$::jsonb
WHERE id = 203;

UPDATE products SET
  description = $d304$Бюджетная сборка для входа в FullHD гейминг.

Абсолютно любые комплектующие ПК можно изменить по Вашим пожеланиям!

Характеристики:

• Процессор: AMD Ryzen 5 5600

• Оперативная память: DDR4 16GB 3200Mhz Kingston

• Видеокарта: NVIDIA RTX3050 8GB

• SSD: M2 NVME 512GB Kingston KC3000

• Блок питания: Phanteks AMP GH450W 80+ Bronze

• Воздушное охлаждение Thermalright Assassin X

• Охлаждение: 2 вертушки

• Корпус: Lian Li Lancool 205 Mesh

⚙️ Полная настройка и сборка под ключ!

✔️ Windows, все необходимые драйвера, программы уже установлены!$d304$,
  config_json = $j304${"basePrice":89990,"baseCpu":"R5 5600","baseGpu":"RTX3050","image":"photo/pc_fh4.jpg","name":"AURUM FHD Starter","description":"Бюджетная сборка для входа в FullHD гейминг.\n\nАбсолютно любые комплектующие ПК можно изменить по Вашим пожеланиям!\n\nХарактеристики:\n\n• Процессор: AMD Ryzen 5 5600\n\n• Оперативная память: DDR4 16GB 3200Mhz Kingston\n\n• Видеокарта: NVIDIA RTX3050 8GB\n\n• SSD: M2 NVME 512GB Kingston KC3000\n\n• Блок питания: Phanteks AMP GH450W 80+ Bronze\n\n• Воздушное охлаждение Thermalright Assassin X\n\n• Охлаждение: 2 вертушки\n\n• Корпус: Lian Li Lancool 205 Mesh\n\n⚙️ Полная настройка и сборка под ключ!\n\n✔️ Windows, все необходимые драйвера, программы уже установлены!","options":{"cpu":[{"name":"AMD Ryzen 5 5600","price":0,"selected":true},{"name":"Intel Core i5-12400F","price":3000},{"name":"AMD Ryzen 5 7600","price":10000},{"name":"Intel Core i5-13400F","price":11000}],"gpu":[{"name":"NVIDIA RTX 3050 8GB","price":0,"selected":true},{"name":"NVIDIA RTX 4060 8GB","price":15000},{"name":"NVIDIA GTX 1660 SUPER 6GB","price":-5000},{"name":"AMD RX 6600 8GB","price":-3000}],"ssd":[{"name":"512GB NVMe SSD","price":0,"selected":true},{"name":"1TB NVMe SSD","price":5000},{"name":"256GB NVMe SSD","price":-3000},{"name":"512GB NVMe SSD + 1TB HDD","price":2000}],"warranty":[{"name":"1 год","price":0,"selected":true},{"name":"2 года","price":5000},{"name":"3 года","price":10000},{"name":"5 лет","price":20000}]}}$j304$::jsonb
WHERE id = 304;

UPDATE products SET
  description = $d302$Отличная сборка для FullHD гейминга с хорошим соотношением цена/производительность.

Абсолютно любые комплектующие ПК можно изменить по Вашим пожеланиям!

Характеристики:

• Процессор: AMD Ryzen 5 7600

• Оперативная память: DDR5 16GB 5600Mhz Kingston

• Видеокарта: NVIDIA RTX4060 8GB

• SSD: M2 NVME 1TB Kingston KC3000

• Блок питания: Phanteks AMP GH550W 80+ Bronze

• Воздушное охлаждение Thermalright Assassin X

• Охлаждение: 2 ARGB вертушки

• Корпус: Lian Li Lancool 205 Mesh

⚙️ Полная настройка и сборка под ключ!

✔️ Windows, все необходимые драйвера, программы уже установлены!$d302$,
  config_json = $j302${"basePrice":119990,"baseCpu":"R5 7600","baseGpu":"RTX4060","image":"photo/pc_fh2.jpg","name":"AURUM FHD Pro","description":"Отличная сборка для FullHD гейминга с хорошим соотношением цена/производительность.\n\nАбсолютно любые комплектующие ПК можно изменить по Вашим пожеланиям!\n\nХарактеристики:\n\n• Процессор: AMD Ryzen 5 7600\n\n• Оперативная память: DDR5 16GB 5600Mhz Kingston\n\n• Видеокарта: NVIDIA RTX4060 8GB\n\n• SSD: M2 NVME 1TB Kingston KC3000\n\n• Блок питания: Phanteks AMP GH550W 80+ Bronze\n\n• Воздушное охлаждение Thermalright Assassin X\n\n• Охлаждение: 2 ARGB вертушки\n\n• Корпус: Lian Li Lancool 205 Mesh\n\n⚙️ Полная настройка и сборка под ключ!\n\n✔️ Windows, все необходимые драйвера, программы уже установлены!","options":{"cpu":[{"name":"AMD Ryzen 5 7600","price":0,"selected":true},{"name":"Intel Core i5-13400F","price":5000},{"name":"AMD Ryzen 7 7700X","price":15000},{"name":"Intel Core i5-13600KF","price":20000}],"gpu":[{"name":"NVIDIA RTX 4060 8GB","price":0,"selected":true},{"name":"NVIDIA RTX 4060 Ti 16GB","price":15000},{"name":"NVIDIA RTX 3050 8GB","price":-8000},{"name":"AMD RX 6600 8GB","price":-10000}],"ssd":[{"name":"1TB NVMe SSD","price":0,"selected":true},{"name":"2TB NVMe SSD","price":8000},{"name":"512GB NVMe SSD","price":-5000},{"name":"1TB NVMe SSD + 1TB HDD","price":2000}],"warranty":[{"name":"1 год","price":0,"selected":true},{"name":"2 года","price":5000},{"name":"3 года","price":10000},{"name":"5 лет","price":20000}]}}$j302$::jsonb
WHERE id = 302;

UPDATE products SET
  description = $d301$Топовая сборка для FullHD гейминга с отличной производительностью.

Абсолютно любые комплектующие ПК можно изменить по Вашим пожеланиям!

Характеристики:

• Процессор: Intel Core i5-13400F

• Оперативная память: DDR4 16GB 3200Mhz Kingston

• Видеокарта: NVIDIA RTX4060 8GB

• SSD: M2 NVME 1TB Kingston KC3000

• Блок питания: Phanteks AMP GH600W 80+ Bronze

• Воздушное охлаждение Thermalright Assassin X

• Охлаждение: 2 ARGB вертушки

• Корпус: Lian Li Lancool 205 Mesh

⚙️ Полная настройка и сборка под ключ!

✔️ Windows, все необходимые драйвера, программы уже установлены!$d301$,
  config_json = $j301${"basePrice":139990,"baseCpu":"i5-13400F","baseGpu":"RTX4060","image":"photo/pc_fh1.jpg","name":"AURUM FHD Ultra","description":"Топовая сборка для FullHD гейминга с отличной производительностью.\n\nАбсолютно любые комплектующие ПК можно изменить по Вашим пожеланиям!\n\nХарактеристики:\n\n• Процессор: Intel Core i5-13400F\n\n• Оперативная память: DDR4 16GB 3200Mhz Kingston\n\n• Видеокарта: NVIDIA RTX4060 8GB\n\n• SSD: M2 NVME 1TB Kingston KC3000\n\n• Блок питания: Phanteks AMP GH600W 80+ Bronze\n\n• Воздушное охлаждение Thermalright Assassin X\n\n• Охлаждение: 2 ARGB вертушки\n\n• Корпус: Lian Li Lancool 205 Mesh\n\n⚙️ Полная настройка и сборка под ключ!\n\n✔️ Windows, все необходимые драйвера, программы уже установлены!","options":{"cpu":[{"name":"Intel Core i5-13400F","price":0,"selected":true},{"name":"AMD Ryzen 5 7600","price":8000},{"name":"Intel Core i5-13600KF","price":15000},{"name":"AMD Ryzen 7 7700X","price":20000}],"gpu":[{"name":"NVIDIA RTX 4060 8GB","price":0,"selected":true},{"name":"NVIDIA RTX 4060 Ti 16GB","price":15000},{"name":"NVIDIA RTX 4070 SUPER 12GB","price":30000},{"name":"AMD RX 7600 8GB","price":-15000}],"ssd":[{"name":"1TB NVMe SSD","price":0,"selected":true},{"name":"2TB NVMe SSD","price":8000},{"name":"512GB NVMe SSD","price":-5000},{"name":"1TB NVMe SSD + 1TB HDD","price":2000}],"warranty":[{"name":"1 год","price":0,"selected":true},{"name":"2 года","price":5000},{"name":"3 года","price":10000},{"name":"5 лет","price":20000}]}}$j301$::jsonb
WHERE id = 301;

UPDATE products SET
  description = $d303$Сбалансированная сборка для комфортного FullHD гейминга.

Абсолютно любые комплектующие ПК можно изменить по Вашим пожеланиям!

Характеристики:

• Процессор: Intel Core i5-12400F

• Оперативная память: DDR4 16GB 3200Mhz Kingston

• Видеокарта: NVIDIA RTX3060 12GB

• SSD: M2 NVME 512GB Kingston KC3000

• Блок питания: Phanteks AMP GH500W 80+ Bronze

• Воздушное охлаждение Thermalright Assassin X

• Охлаждение: 2 вертушки

• Корпус: Lian Li Lancool 205 Mesh

⚙️ Полная настройка и сборка под ключ!

✔️ Windows, все необходимые драйвера, программы уже установлены!$d303$,
  config_json = $j303${"basePrice":99990,"baseCpu":"i5-12400F","baseGpu":"RTX3060","image":"photo/pc_fh3.jpg","name":"AURUM FHD Core","description":"Сбалансированная сборка для комфортного FullHD гейминга.\n\nАбсолютно любые комплектующие ПК можно изменить по Вашим пожеланиям!\n\nХарактеристики:\n\n• Процессор: Intel Core i5-12400F\n\n• Оперативная память: DDR4 16GB 3200Mhz Kingston\n\n• Видеокарта: NVIDIA RTX3060 12GB\n\n• SSD: M2 NVME 512GB Kingston KC3000\n\n• Блок питания: Phanteks AMP GH500W 80+ Bronze\n\n• Воздушное охлаждение Thermalright Assassin X\n\n• Охлаждение: 2 вертушки\n\n• Корпус: Lian Li Lancool 205 Mesh\n\n⚙️ Полная настройка и сборка под ключ!\n\n✔️ Windows, все необходимые драйвера, программы уже установлены!","options":{"cpu":[{"name":"Intel Core i5-12400F","price":0,"selected":true},{"name":"AMD Ryzen 5 5600","price":-3000},{"name":"Intel Core i5-13400F","price":8000},{"name":"AMD Ryzen 5 7600","price":10000}],"gpu":[{"name":"NVIDIA RTX 3060 12GB","price":0,"selected":true},{"name":"NVIDIA RTX 3060 Ti 8GB","price":10000},{"name":"NVIDIA RTX 4060 8GB","price":15000},{"name":"AMD RX 6600 8GB","price":3000}],"ssd":[{"name":"512GB NVMe SSD","price":0,"selected":true},{"name":"1TB NVMe SSD","price":5000},{"name":"2TB NVMe SSD","price":13000},{"name":"512GB NVMe SSD + 1TB HDD","price":2000}],"warranty":[{"name":"1 год","price":0,"selected":true},{"name":"2 года","price":5000},{"name":"3 года","price":10000},{"name":"5 лет","price":20000}]}}$j303$::jsonb
WHERE id = 303;

COMMIT;
