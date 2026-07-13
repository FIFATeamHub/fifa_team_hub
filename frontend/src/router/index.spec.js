import { describe, it, expect, vi, beforeEach } from 'vitest'

vi.mock('vue-router', async (importOriginal) => {
  const actual = await importOriginal()
  return { ...actual, createWebHistory: actual.createMemoryHistory }
})

vi.mock('../stores/auth', () => ({
  useAuthStore: vi.fn()
}))

import { useAuthStore } from '../stores/auth'
import router from './index'

describe('router - bloqueio de rotas guest', () => {
  beforeEach(() => {
    vi.mocked(useAuthStore).mockReset()
  })

  it('usuário autenticado tentando acessar /login é redirecionado para dashboard', async () => {
    vi.mocked(useAuthStore).mockReturnValue({
      isAuthenticated: true,
      token: 'fake-token',
      user: { role: 'USER' },
      fetchMe: vi.fn(),
      logout: vi.fn(),
    })

    await router.push('/login')

    expect(router.currentRoute.value.name).toBe('dashboard')
  })

  it('visitante não autenticado consegue acessar /login normalmente', async () => {
    vi.mocked(useAuthStore).mockReturnValue({
      isAuthenticated: false,
      token: null,
      user: null,
      fetchMe: vi.fn(),
      logout: vi.fn(),
    })

    await router.push('/login')

    expect(router.currentRoute.value.name).toBe('login')
  })
})
