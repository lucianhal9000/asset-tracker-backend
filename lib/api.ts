import axios, { AxiosError } from 'axios'

export interface Asset {
  id: string
  name: string
  asset_type: 'vehicle' | 'equipment' | 'person'
  status: 'active' | 'inactive' | 'lost'
  description: string
  created_at: string
  updated_at: string
  latest_location: {
    latitude: string
    longitude: string
    timestamp: string
  } | null
}

export interface Location {
  id: string
  asset: string
  latitude: string
  longitude: string
  timestamp: string
}

export interface AssetStats {
  total: number
  active: number
  inactive: number
  lost: number
}

const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL,
})

api.interceptors.request.use((config) => {
  if (typeof window === 'undefined') return config
  const token = window.localStorage.getItem('access_token')
  if (token) {
    config.headers = config.headers ?? {}
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

api.interceptors.response.use(
  (response) => response,
  (error: AxiosError) => {
    if (typeof window !== 'undefined' && error.response?.status === 401) {
      window.localStorage.removeItem('access_token')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

export const auth = {
  async login(username: string, password: string) {
    const res = await api.post('/token/', { username, password })
    const access = (res.data as { access?: string }).access
    if (typeof window !== 'undefined' && access) {
      window.localStorage.setItem('access_token', access)
    }
    return res.data
  },
}

export const assets = {
  async list(filters?: { status?: string; asset_type?: string }) {
    const res = await api.get<Asset[]>('/assets/', { params: filters })
    return res.data
  },

  async create(data: Partial<Asset> & Record<string, unknown>) {
    const res = await api.post<Asset>('/assets/', data)
    return res.data
  },

  async update(id: string, data: Partial<Asset> & Record<string, unknown>) {
    const res = await api.patch<Asset>(`/assets/${id}/`, data)
    return res.data
  },

  async delete(id: string) {
    const res = await api.delete(`/assets/${id}/`)
    return res.data
  },

  async stats() {
    const res = await api.get<AssetStats>('/assets/stats/')
    return res.data
  },
}

export const locations = {
  async listByAsset(assetId: string) {
    const res = await api.get<Location[]>('/locations/', {
      params: { asset_id: assetId },
    })
    return res.data
  },
}

export const telemetry = {
  async send(payload: {
    asset_id: string
    latitude: string
    longitude: string
    raw_payload?: string
  }) {
    const res = await api.post('/telemetry/', payload)
    return res.data
  },
}

export default api
