import { describe, it, expect, vi, beforeEach } from 'vitest'
import { useDocuments } from '@/composables/useDocuments'

// Simula o módulo api.js inteiro — nenhuma chamada real ao backend
vi.mock('@/services/api', () => ({
  default: {
    get: vi.fn(),
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

    // Espiona o clique no elemento <a>
    const clickSpy = vi.spyOn(HTMLAnchorElement.prototype, 'click')
      .mockImplementation(() => {})

    const { downloadDocument } = useDocuments()
    await downloadDocument('doc-123', 'relatorio.pdf')

    expect(clickSpy).toHaveBeenCalled()
  })

  it('downloadDocument deve lançar erro se o backend retornar 410', async () => {
    vi.mocked(api.get).mockRejectedValue({ response: { status: 410 } })

    const { downloadDocument } = useDocuments()

    await expect(downloadDocument('doc-999', 'arquivo.pdf'))
      .rejects
      .toThrow('Este documento foi removido permanentemente.')
  })

  it('downloadDocument deve lançar erro se o serviço de armazenamento estiver indisponível (503)', async () => {
    vi.mocked(api.get).mockRejectedValue({ response: { status: 503 } })

    const { downloadDocument } = useDocuments()

    await expect(downloadDocument('doc-999', 'arquivo.pdf'))
      .rejects
      .toThrow('Serviço de armazenamento temporariamente indisponível. Tente novamente em instantes.')
  })

})
