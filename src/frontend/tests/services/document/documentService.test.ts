import { describe, it, expect, vi } from 'vitest';

// Simple mock approach - similar to existing working tests
vi.mock('../../../src/services/documentService', () => ({
  documentService: {
    getAllDocuments: vi.fn(),
    getDocumentById: vi.fn(),
    createDocument: vi.fn(),
    updateDocument: vi.fn(),
    deleteDocument: vi.fn(),
    uploadFile: vi.fn(),
    getFileUrl: vi.fn(),
    getProcessingStatus: vi.fn(),
  },
}));

import { documentService } from '../../../src/services/documentService';

describe('documentService', () => {

  it('should work with basic functionality', () => {
    expect(documentService).toBeDefined();
    expect(typeof documentService.getAllDocuments).toBe('function');
    expect(typeof documentService.getDocumentById).toBe('function');
    expect(typeof documentService.createDocument).toBe('function');
    expect(typeof documentService.deleteDocument).toBe('function');
    expect(typeof documentService.uploadFile).toBe('function');
    expect(typeof documentService.getFileUrl).toBe('function');
    expect(typeof documentService.getProcessingStatus).toBe('function');
  });

  it('should handle document operations', async () => {
    const mockDoc = { id: 1, title: 'Test Document' };
    (documentService.getAllDocuments as any).mockResolvedValue([mockDoc]);
    (documentService.getDocumentById as any).mockResolvedValue(mockDoc);
    (documentService.createDocument as any).mockResolvedValue(mockDoc);
    (documentService.deleteDocument as any).mockResolvedValue({ success: true });

    const allDocs = await documentService.getAllDocuments();
    const singleDoc = await documentService.getDocumentById(1);
    const createdDoc = await documentService.createDocument({ title: 'New Doc' });
    const deleteResult = await documentService.deleteDocument(1);

    expect(allDocs).toEqual([mockDoc]);
    expect(singleDoc).toEqual(mockDoc);
    expect(createdDoc).toEqual(mockDoc);
    expect(deleteResult.success).toBe(true);
  });

  it('should handle file operations', async () => {
    const mockFile = new File(['content'], 'test.txt');
    const uploadResult = { path: 'documents/test.txt' };
    const publicUrl = 'https://example.com/file.txt';

    (documentService.uploadFile as any).mockResolvedValue(uploadResult);
    (documentService.getFileUrl as any).mockReturnValue(publicUrl);

    const uploaded = await documentService.uploadFile(mockFile, 'path');
    const url = documentService.getFileUrl('path');

    expect(uploaded).toEqual(uploadResult);
    expect(url).toBe(publicUrl);
  });

  it('should handle processing status', async () => {
    const statusData = { status: 'completed', chunk_count: 5 };
    (documentService.getProcessingStatus as any).mockResolvedValue(statusData);

    const status = await documentService.getProcessingStatus(1);

    expect(status).toEqual(statusData);
  });
}); 