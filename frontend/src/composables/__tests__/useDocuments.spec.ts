import { describe, it, expect, vi, beforeEach } from 'vitest'
import { useDocuments } from '@/composables/useDocuments'

// Simula o módulo api.js inteiro — nenhuma chamada real ao backend
vi.mock('@/services/api', () => ({
  default: {
    get: vi.fn(),
    head: vi.fn(),
  }
}))

// Importa o mock para configurar os retornos nos testes
import api from '@/services/api'

describe('useDocuments', () => {

  beforeEach(() => {
    // Limpa os mocks antes de cada teste para não vazar dados entre eles
    vi.clearAllMocks()
  })

  it('getDownloadUrl deve retornar a URL assinada do backend', async () => {
    const mockUrl = 'https://storage.googleapis.com/bucket/doc.pdf?sign=abc'

    // Configura o que o axios.get vai "fingir" retornar
    vi.mocked(api.get).mockResolvedValue({ data: { url: mockUrl } })

    const { getDownloadUrl } = useDocuments()
    const url = await getDownloadUrl('doc-123')

    expect(url).toBe(mockUrl)
    expect(url).toContain('storage.googleapis.com')
  })

  it('downloadDocument deve simular o clique no link', async () => {
    const mockUrl = 'https://storage.googleapis.com/bucket/doc.pdf?sign=abc'

    vi.mocked(api.get).mockResolvedValue({ data: { url: mockUrl } })
    vi.mocked(api.head).mockResolvedValue({ status: 200 })

    // Espiona o clique no elemento <a>
    const clickSpy = vi.spyOn(HTMLAnchorElement.prototype, 'click')
      .mockImplementation(() => {})

    const { downloadDocument } = useDocuments()
    await downloadDocument('doc-123', 'relatorio.pdf')

    expect(clickSpy).toHaveBeenCalled()
  })

  it('downloadDocument deve lançar erro se URL retornar 410', async () => {
    vi.mocked(api.get).mockResolvedValue({ data: { url: 'https://expired-url' } })
    vi.mocked(api.head).mockRejectedValue({ response: { status: 410 } })

    const { downloadDocument } = useDocuments()

    // Espera que a função jogue um erro
    await expect(downloadDocument('doc-999', 'arquivo.pdf'))
      .rejects
      .toThrow('Este documento foi removido permanentemente.')
  })

})
