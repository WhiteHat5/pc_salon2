/**
 * Шаблоны описаний и наборов опций конфигуратора (как эталонные карточки витрины:
 * 4K — как AURUM 4K Pro, 2K — как AURUM 2K Ultra, Full HD — как AURUM FHD Ultra).
 * Подключается из products.html до основного скрипта админки.
 */
(function () {
  window.AURUM_ADMIN_DESC_PRESETS = {
    '4k': `Самый мощный вариант для 4К гейминга на современном процессоре Ryzen с видеокартой Nvidia 5000 серии.

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

✔️ Windows, все необходимые драйвера, программы уже установлены!`,
    '2k': `Топовая сборка для 2К гейминга с максимальной производительностью.

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

✔️ Windows, все необходимые драйвера, программы уже установлены!`,
    fullhd: `Топовая сборка для FullHD гейминга с отличной производительностью.

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

✔️ Windows, все необходимые драйвера, программы уже установлены!`,
  };

  window.AURUM_ADMIN_OPTION_PRESETS = {
    '4k': {
      cpu: [
        { name: 'Intel Core i9-13900K', price: 0, selected: true },
        { name: 'AMD Ryzen 9 9950X3D', price: 25000 },
        { name: 'Intel Core i9-14900K', price: 15000 },
        { name: 'AMD Ryzen 9 7950X3D', price: 20000 },
      ],
      gpu: [
        { name: 'NVIDIA RTX 4090 24GB', price: 0, selected: true },
        { name: 'NVIDIA RTX 5090 32GB', price: 50000 },
        { name: 'NVIDIA RTX 4080 SUPER 16GB', price: -20000 },
        { name: 'AMD RX 7900 XTX 24GB', price: -15000 },
      ],
      ssd: [
        { name: '2TB NVMe SSD', price: 0, selected: true },
        { name: '1TB NVMe SSD', price: -8000 },
        { name: '4TB NVMe SSD', price: 15000 },
        { name: '2TB NVMe SSD + 4TB HDD', price: 5000 },
      ],
      warranty: [
        { name: '1 год', price: 0, selected: true },
        { name: '2 года', price: 5000 },
        { name: '3 года', price: 10000 },
        { name: '5 лет', price: 20000 },
      ],
    },
    '2k': {
      cpu: [
        { name: 'Intel Core i7-13700KF', price: 0, selected: true },
        { name: 'AMD Ryzen 7 7800X3D', price: 15000 },
        { name: 'Intel Core i7-14700KF', price: 10000 },
        { name: 'AMD Ryzen 9 7900X', price: 20000 },
      ],
      gpu: [
        { name: 'NVIDIA RTX 4080 16GB', price: 0, selected: true },
        { name: 'NVIDIA RTX 4080 SUPER 16GB', price: 12000 },
        { name: 'NVIDIA RTX 4090 24GB', price: 35000 },
        { name: 'NVIDIA RTX 4070 TI SUPER 16GB', price: -15000 },
      ],
      ssd: [
        { name: '2TB NVMe SSD', price: 0, selected: true },
        { name: '1TB NVMe SSD', price: -8000 },
        { name: '4TB NVMe SSD', price: 15000 },
        { name: '2TB NVMe SSD + 4TB HDD', price: 5000 },
      ],
      warranty: [
        { name: '1 год', price: 0, selected: true },
        { name: '2 года', price: 5000 },
        { name: '3 года', price: 10000 },
        { name: '5 лет', price: 20000 },
      ],
    },
    fullhd: {
      cpu: [
        { name: 'Intel Core i5-13400F', price: 0, selected: true },
        { name: 'AMD Ryzen 5 7600', price: 8000 },
        { name: 'Intel Core i5-13600KF', price: 15000 },
        { name: 'AMD Ryzen 7 7700X', price: 20000 },
      ],
      gpu: [
        { name: 'NVIDIA RTX 4060 8GB', price: 0, selected: true },
        { name: 'NVIDIA RTX 4060 Ti 16GB', price: 15000 },
        { name: 'NVIDIA RTX 4070 SUPER 12GB', price: 30000 },
        { name: 'AMD RX 7600 8GB', price: -15000 },
      ],
      ssd: [
        { name: '1TB NVMe SSD', price: 0, selected: true },
        { name: '2TB NVMe SSD', price: 8000 },
        { name: '512GB NVMe SSD', price: -5000 },
        { name: '1TB NVMe SSD + 1TB HDD', price: 2000 },
      ],
      warranty: [
        { name: '1 год', price: 0, selected: true },
        { name: '2 года', price: 5000 },
        { name: '3 года', price: 10000 },
        { name: '5 лет', price: 20000 },
      ],
    },
  };
})();
