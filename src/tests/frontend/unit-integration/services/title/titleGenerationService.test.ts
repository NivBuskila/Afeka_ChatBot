import { describe, it, expect, vi, beforeEach, beforeAll } from 'vitest';

// Mock environment
vi.stubEnv('VITE_BACKEND_URL', 'http://localhost:8000');

// Create a proper fetch mock function that handles the apiRequest logic
const createMockResponse = (data: any, ok: boolean = true, status: number = 200) => {
  return Promise.resolve({
    ok,
    status,
    json: () => Promise.resolve(data),
    text: () => Promise.resolve(JSON.stringify(data)),
    headers: {
      get: (key: string) => {
        if (key.toLowerCase() === 'content-type') return 'application/json';
        return null;
      }
    }
  } as Response);
};

// Mock global fetch with vi.fn()
const mockFetch = vi.fn();

// Use beforeAll to ensure proper setup
beforeAll(() => {
  global.fetch = mockFetch;
});

import { titleGenerationService, Message } from '../../../src/services/titleGenerationService';

describe('titleGenerationService', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mockFetch.mockClear();
  });

  const mockMessages: Message[] = [
    {
      id: '1',
      type: 'user',
      content: 'שלום, אני רוצה לדעת על קורסי תכנות',
      timestamp: '2024-01-01T10:00:00Z',
    },
    {
      id: '2',
      type: 'bot',
      content: 'שלום! אשמח לעזור לך עם קורסי התכנות שלנו',
      timestamp: '2024-01-01T10:01:00Z',
    },
    {
      id: '3',
      type: 'user',
      content: 'איזה קורסים יש לכם?',
      timestamp: '2024-01-01T10:02:00Z',
    },
  ];

  describe('generateTitle', () => {
    it('should generate title successfully', async () => {
      const mockResponse = { title: 'קורסי תכנות במכללה' };

      mockFetch.mockResolvedValue({
        ok: true,
        status: 200,
        json: vi.fn().mockResolvedValue(mockResponse),
        text: vi.fn().mockResolvedValue(JSON.stringify(mockResponse)),
      } as any);

      const result = await titleGenerationService.generateTitle(mockMessages);

      expect(result).toBe('קורסי תכנות במכללה');
      expect(mockFetch).toHaveBeenCalledWith(
        'http://localhost:8000/api/generate-title',
        expect.objectContaining({
          method: 'POST',
          headers: expect.objectContaining({
            'Content-Type': 'application/json',
          }),
          body: expect.stringContaining('"prompt"')
        })
      );
    });

    it('should truncate long titles', async () => {
      const longTitle = 'זהו כותרת ארוכה מאוד שצריכה להיחתך כי היא חורגת מהמקסימום המותר של חמישים תווים בלבד';
      const mockResponse = { title: longTitle };

      mockFetch.mockResolvedValue({
        ok: true,
        status: 200,
        json: vi.fn().mockResolvedValue(mockResponse),
        text: vi.fn().mockResolvedValue(JSON.stringify(mockResponse)),
      } as any);

      const result = await titleGenerationService.generateTitle(mockMessages, 50);

      expect(result).toBe(longTitle.substring(0, 47) + '...');
      expect(result!.length).toBeLessThanOrEqual(50);
    });

    it('should return null for insufficient messages', async () => {
      const shortMessages: Message[] = [
        {
          id: '1',
          type: 'user',
          content: 'שלום',
          timestamp: '2024-01-01T10:00:00Z',
        },
      ];

      const result = await titleGenerationService.generateTitle(shortMessages);

      expect(result).toBeNull();
      expect(mockFetch).not.toHaveBeenCalled();
    });

    it('should return null for empty messages', async () => {
      const result = await titleGenerationService.generateTitle([]);

      expect(result).toBeNull();
      expect(mockFetch).not.toHaveBeenCalled();
    });

    it('should handle API errors gracefully', async () => {
      mockFetch.mockRejectedValue(new Error('Network error'));

      const result = await titleGenerationService.generateTitle(mockMessages);

      expect(result).toBeNull();
    });

    it('should handle empty API response', async () => {
      mockFetch.mockResolvedValue({
        ok: true,
        status: 200,
        json: vi.fn().mockResolvedValue({}),
        text: vi.fn().mockResolvedValue('{}'),
      } as any);

      const result = await titleGenerationService.generateTitle(mockMessages);

      expect(result).toBeNull();
    });

    it('should handle API failure status', async () => {
      mockFetch.mockResolvedValue({
        ok: false,
        status: 500,
        json: vi.fn().mockResolvedValue({}),
        text: vi.fn().mockResolvedValue('{}'),
      } as any);

      const result = await titleGenerationService.generateTitle(mockMessages);

      expect(result).toBeNull();
    });

    it('should filter empty messages', async () => {
      const messagesWithEmpty: Message[] = [
        ...mockMessages,
        {
          id: '4',
          type: 'user',
          content: '   ',
          timestamp: '2024-01-01T10:03:00Z',
        },
      ];

      const mockResponse = { title: 'קורסי תכנות' };
      mockFetch.mockResolvedValue({
        ok: true,
        status: 200,
        json: vi.fn().mockResolvedValue(mockResponse),
        text: vi.fn().mockResolvedValue(JSON.stringify(mockResponse)),
      } as any);

      const result = await titleGenerationService.generateTitle(messagesWithEmpty);

      expect(result).toBe('קורסי תכנות');
      if (mockFetch.mock.calls.length > 0) {
        const requestBody = JSON.parse(mockFetch.mock.calls[0][1].body);
        expect(requestBody.prompt).not.toContain('   ');
      }
    });
  });

  describe('generateSimpleTitle', () => {
    it('should generate simple title from first message', () => {
      const firstMessage = 'שלום, אני רוצה לדעת על קורסי תכנות במכללה';

      const result = titleGenerationService.generateSimpleTitle(firstMessage);

      expect(result).toBe('שלום, אני רוצה לדעת על קורסי תכנות במכללה');
    });

    it('should remove common words', () => {
      const firstMessage = 'אני רוצה לדעת איך להירשם לקורס';

      const result = titleGenerationService.generateSimpleTitle(firstMessage);

      expect(result).toBe('אני רוצה לדעת איך להירשם לקורס');
    });

    it('should truncate long messages', () => {
      const longMessage = 'זהו הודעה ארוכה מאוד שמכילה הרבה מילים ותוכן שצריך להיחתך';

      const result = titleGenerationService.generateSimpleTitle(longMessage, 30);

      expect(result.length).toBeLessThanOrEqual(30);
      expect(result).toMatch(/\.\.\.$/);
    });

    it('should handle empty message', () => {
      const result = titleGenerationService.generateSimpleTitle('');

      expect(result).toMatch(/שיחה חדשה - \d{1,2}\.\d{1,2}\.\d{4}/);
    });

    it('should handle whitespace-only message', () => {
      const result = titleGenerationService.generateSimpleTitle('   ');

      expect(result).toMatch(/שיחה חדשה - \d{1,2}\.\d{1,2}\.\d{4}/);
    });

    it('should clean multiple spaces', () => {
      const messageWithSpaces = 'שלום    איך    אתה';

      const result = titleGenerationService.generateSimpleTitle(messageWithSpaces);

      expect(result).toBe('שלום איך אתה');
    });
  });

  describe('shouldUpdateTitle', () => {
    it('should update every 2 messages for early conversation', () => {
      expect(titleGenerationService.shouldUpdateTitle('default', 2)).toBe(true);
      expect(titleGenerationService.shouldUpdateTitle('default', 4)).toBe(true);
      expect(titleGenerationService.shouldUpdateTitle('default', 6)).toBe(true);
    });

    it('should not update on odd messages for early conversation', () => {
      expect(titleGenerationService.shouldUpdateTitle('default', 1)).toBe(false);
      expect(titleGenerationService.shouldUpdateTitle('default', 3)).toBe(false);
      expect(titleGenerationService.shouldUpdateTitle('default', 5)).toBe(false);
    });

    it('should update every 3 messages for mid conversation', () => {
      expect(titleGenerationService.shouldUpdateTitle('default', 9)).toBe(true);
      expect(titleGenerationService.shouldUpdateTitle('default', 12)).toBe(true);
    });

    it('should update every 5 messages for long conversation', () => {
      expect(titleGenerationService.shouldUpdateTitle('default', 15)).toBe(true);
      expect(titleGenerationService.shouldUpdateTitle('default', 20)).toBe(true);
    });

    it('should not update when not divisible', () => {
      expect(titleGenerationService.shouldUpdateTitle('default', 7)).toBe(false);
      expect(titleGenerationService.shouldUpdateTitle('default', 14)).toBe(false);
      expect(titleGenerationService.shouldUpdateTitle('default', 17)).toBe(false);
    });
  });

  describe('isDefaultTitle', () => {
    it('should identify default titles', () => {
      expect(titleGenerationService.isDefaultTitle(null)).toBe(true);
      expect(titleGenerationService.isDefaultTitle('Chat 1')).toBe(true);
      expect(titleGenerationService.isDefaultTitle('שיחה חדשה')).toBe(true);
      expect(titleGenerationService.isDefaultTitle('New Chat')).toBe(true);
      expect(titleGenerationService.isDefaultTitle('19/06/2024')).toBe(true);
      expect(titleGenerationService.isDefaultTitle('שיחה 1')).toBe(true);
    });

    it('should not identify custom titles as default', () => {
      expect(titleGenerationService.isDefaultTitle('קורסי תכנות')).toBe(false);
      expect(titleGenerationService.isDefaultTitle('שאלה על מטלות')).toBe(false);
      expect(titleGenerationService.isDefaultTitle('Programming courses')).toBe(false);
    });

    it('should handle edge cases', () => {
      expect(titleGenerationService.isDefaultTitle('')).toBe(true);
      expect(titleGenerationService.isDefaultTitle('   ')).toBe(false);
      expect(titleGenerationService.isDefaultTitle('Chat')).toBe(false);
    });
  });
}); 