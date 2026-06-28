import { describe, it, expect, vi } from 'vitest'
import { useDocuments } from '@/composables/useDocuments'
import axios from 'axios'

vi.mock('axios', () => ({
  default: {
    get: vi.fn(),
    head: vi.fn()
  }
}))

describe('useDocuments com GCS', () => {
  it('deve buscar URL assinada do documento', async () => {
    const mockUrl = 'https://storage.googleapis.com/bucket/.../signed-url'
    vi.mocked(axios.get).mockResolvedValue({ data: { url: mockUrl } })
 
    const { getDownloadUrl } = useDocuments()
    const url = await getDownloadUrl('doc-123')
 
    expect(url).toBe(mockUrl)
    expect(url).toContain('storage.googleapis.com')
  })
 
  it('deve fazer download usando URL assinada e verificar validade', async () => {
    const mockUrl = 'https://storage.googleapis.com/bucket/.../signed-url'
    vi.mocked(axios.get).mockResolvedValue({ data: { url: mockUrl } })
    vi.mocked(axios.head).mockResolvedValue({ status: 200 })
    
    const { downloadDocument } = useDocuments()
    
    const linkClickSpy = vi.spyOn(HTMLAnchorElement.prototype, 'click')
    
    await downloadDocument('doc-123', 'test.pdf')
    
    expect(vi.mocked(axios.head)).toHaveBeenCalledWith(mockUrl, expect.any(Object))
    expect(linkClickSpy).toHaveBeenCalled()
  })
})