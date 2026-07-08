import { describe, it, expect, vi } from 'vitest'
import { useDocuments } from '@/composables/useDocuments'
 
describe('useDocuments com GCS', () => {
  it('deve buscar URL assinada do documento', async () => {
    // Mock axios
    const mockUrl = 'https://storage.googleapis.com/bucket/.../signed-url'
    vi.mock('axios', () => ({
      default: {
        get: vi.fn().mockResolvedValue({ data: { url: mockUrl } })
      }
    }))
 
    const { getDownloadUrl } = useDocuments()
    const url = await getDownloadUrl('doc-123')
 
    expect(url).toBe(mockUrl)
    expect(url).toContain('storage.googleapis.com')
  })
 
  it('deve fazer download usando URL assinada', async () => {
    const { downloadDocument } = useDocuments()
    
    // Mock do DOM e axios
    const linkClickSpy = vi.spyOn(HTMLAnchorElement.prototype, 'click')
    
    await downloadDocument('doc-123', 'test.pdf')
    
    expect(linkClickSpy).toHaveBeenCalled()
  })
})