/**
 * API модуль для работы с backend
 * По умолчанию: FastAPI на http://127.0.0.1:8000/api
 * Опционально: window.API_URL или localStorage.API_URL
 */

let API_BASE_URL;
const DEFAULT_FASTAPI_BASE_URL = 'http://127.0.0.1:8000/api';

if (window.API_URL) {
  API_BASE_URL = window.API_URL.trim().replace(/\/+$/, '');
} else if (window.localStorage && localStorage.getItem('API_URL')) {
  API_BASE_URL = localStorage.getItem('API_URL').trim().replace(/\/+$/, '');
} else {
  const { origin, pathname, protocol, hostname } = window.location;

  if (protocol === 'file:') {
    API_BASE_URL = DEFAULT_FASTAPI_BASE_URL;
  } else if (hostname === 'localhost' || hostname === '127.0.0.1' || hostname === '[::1]' || hostname === '::1') {
    if (window.location.port === '8000' || window.location.port === '8001') {
      API_BASE_URL = `${origin.replace(/\/$/, '')}/api`;
    } else if (pathname.includes('/pc_salon/')) {
      // Локальная статика не на порту API: используем стандартный FastAPI endpoint.
      API_BASE_URL = DEFAULT_FASTAPI_BASE_URL;
    } else {
      API_BASE_URL = `${origin.replace(/\/$/, '')}/api`;
    }
  } else if (pathname.includes('/pc_salon/')) {
    API_BASE_URL = `${origin.replace(/\/$/, '')}/api`;
  } else {
    console.warn('API URL не задан явно. Используется путь /api текущего origin.');
    API_BASE_URL = `${origin.replace(/\/$/, '')}/api`;
  }
}

function asArray(maybe) {
  if (Array.isArray(maybe)) return maybe;
  return [];
}

async function apiRequest(endpoint, options = {}) {
    const url = `${API_BASE_URL}/${endpoint}`;
    const {
        method: methodOpt,
        headers: optHeaders,
        body: bodyOpt,
        ...rest
    } = options;
    const method = (methodOpt || 'GET').toUpperCase();

    const headers = {};
    if (method !== 'GET' && method !== 'HEAD') {
        headers['Content-Type'] = 'application/json';
    }
    if (String(API_BASE_URL).toLowerCase().includes('ngrok')) {
        headers['ngrok-skip-browser-warning'] = 'true';
    }
    if (optHeaders) {
        Object.assign(headers, optHeaders);
    }

    const config = {
        method,
        headers,
        ...rest
    };
    if (bodyOpt !== undefined) {
        config.body = bodyOpt;
    }

    if (config.body && typeof config.body === 'object') {
        config.body = JSON.stringify(config.body);
    }

    try {
        const response = await fetch(url, config);
        const text = await response.text();

        let data;
        try {
            data = text ? JSON.parse(text) : {};
        } catch (jsonError) {
            console.error('Не удалось распарсить JSON. Ответ сервера:', text.substring(0, 200));
            throw new Error('Сервер вернул некорректный JSON или другой формат ответа.');
        }

        if (!response.ok) {
            throw new Error(data.error || `HTTP ${response.status}: ${response.statusText}`);
        }

        return data;
    } catch (error) {
        if (error.name === 'TypeError' && error.message.includes('Failed to fetch')) {
            throw new Error('Нет соединения с сервером. Проверьте интернет или URL API.');
        }
        throw error;
    }
}

const CategoriesAPI = {
    async getAll() {
        const result = await apiRequest('categories');
        const raw = result.categories !== undefined && result.categories !== null
          ? result.categories
          : result.data;
        return asArray(raw);
    }
};

const ProductsAPI = {
    async getAll() {
        const result = await apiRequest('products');
        const raw = result.products !== undefined && result.products !== null
          ? result.products
          : result.data;
        return asArray(raw);
    },

    async getByCategory(categoryId) {
        const result = await apiRequest(`products?category=${categoryId}`);
        const raw = result.products !== undefined && result.products !== null
          ? result.products
          : result.data;
        return asArray(raw);
    },

    async getById(productId) {
        const result = await apiRequest(`products?id=${productId}`);
        return result.product || result.data || null;
    }
};

const UsersAPI = {
    async createOrUpdate(userData) {
        const result = await apiRequest('users', {
            method: 'POST',
            body: userData
        });
        return result.user || result.data;
    },

    async getByTelegramId(telegramId) {
        try {
            const result = await apiRequest(`users?telegram_id=${telegramId}`);
            return result.user || result.data || null;
        } catch (error) {
            if (error.message.includes('404') || error.message.includes('Not Found')) {
                return null;
            }
            throw error;
        }
    },

    async getByPhone(phone) {
        if (!phone) return null;
        try {
            const result = await apiRequest(`users?phone=${encodeURIComponent(phone)}`);
            return result.user || result.data || null;
        } catch (error) {
            if (error.message.includes('400')) {
                return null;
            }
            throw error;
        }
    }
};

const OrdersAPI = {
    async create(orderData) {
        const result = await apiRequest('orders', {
            method: 'POST',
            body: orderData
        });
        return result.order || result.data;
    },

    async getByUser(userId) {
        const result = await apiRequest(`orders?user_id=${userId}`);
        return result.orders || result.data || [];
    },

    async getByTelegramId(telegramId) {
        try {
            const result = await apiRequest(`orders?telegram_id=${telegramId}`);
            const orders = result.orders || result.data || [];
            if (!Array.isArray(orders)) {
                console.warn('OrdersAPI.getByTelegramId: result is not an array:', orders);
                return [];
            }
            return orders;
        } catch (error) {
            console.error('OrdersAPI.getByTelegramId error:', error);
            if (error.message && (error.message.includes('404') || error.message.includes('не найден'))) {
                return [];
            }
            throw error;
        }
    },

    async getByPhone(phone) {
        if (!phone) return [];
        try {
            const result = await apiRequest(`orders?phone=${encodeURIComponent(phone)}`);
            const orders = result.orders || result.data || [];
            return Array.isArray(orders) ? orders : [];
        } catch (error) {
            console.warn('OrdersAPI.getByPhone:', error);
            return [];
        }
    },

    async userCancel(orderId, telegramId) {
        if (orderId == null || telegramId == null) {
            throw new Error('Не указан заказ или Telegram ID');
        }
        const result = await apiRequest(`orders/${encodeURIComponent(String(orderId))}/user-cancel`, {
            method: 'POST',
            body: { telegram_id: Number(telegramId) },
        });
        return result.order || result.data || result;
    }
};

const ReviewsAPI = {
    async create(reviewData) {
        const result = await apiRequest('reviews', {
            method: 'POST',
            body: reviewData
        });
        return result.data || result.review;
    },

    async getByUser(userId) {
        const result = await apiRequest(`reviews?user_id=${userId}`);
        return result.reviews || result.data || [];
    },

    async getByTelegramId(telegramId) {
        if (telegramId == null) return [];
        const result = await apiRequest(`reviews?telegram_id=${telegramId}`);
        return result.reviews || result.data || [];
    },

    async getByOrder(orderId) {
        const result = await apiRequest(`reviews?order_id=${orderId}`);
        return result.reviews || result.data || [];
    },

    async getPublished() {
        const result = await apiRequest('reviews?published=true');
        return result.reviews || result.data || [];
    },

    async listAdmin() {
        const result = await apiRequest('reviews?admin=1');
        return result.reviews || result.data || [];
    },

    async setPublished(reviewId, isPublished) {
        const result = await apiRequest(`reviews/${reviewId}`, {
            method: 'PATCH',
            body: { is_published: !!isPublished }
        });
        return result.data || result;
    }
};

const CertificatesAPI = {
    async getStatus(telegramId) {
        if (telegramId == null) throw new Error('telegram_id обязателен');
        return await apiRequest(`certificates?telegram_id=${telegramId}`);
    },

    async activate(payload) {
        return await apiRequest('certificates', {
            method: 'POST',
            body: payload
        });
    }
};

const BonusLedgerAPI = {
    async getByTelegramId(telegramId) {
        if (telegramId == null) return [];
        const result = await apiRequest(`bonus-ledger?telegram_id=${telegramId}`);
        const rows = result.entries || result.data || [];
        return Array.isArray(rows) ? rows : [];
    }
};

const UserStateAPI = {
    async getByTelegramId(telegramId) {
        if (telegramId == null) return null;
        const result = await apiRequest(`user-state?telegram_id=${telegramId}`);
        return result.state || result.data || null;
    },
    async save(payload) {
        const result = await apiRequest('user-state', {
            method: 'POST',
            body: payload
        });
        return result.state || result.data || null;
    }
};

window.API = {
    categories: CategoriesAPI,
    products: ProductsAPI,
    users: UsersAPI,
    orders: OrdersAPI,
    reviews: ReviewsAPI,
    certificates: CertificatesAPI,
    bonusLedger: BonusLedgerAPI,
    userState: UserStateAPI,
    baseUrl: API_BASE_URL
};

console.log('API инициализирован. Базовый URL:', API_BASE_URL);
