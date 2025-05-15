import fs from 'node:fs';
import { TEST_DB_PATH, cleanupTestDB, createMockMessage } from './utils';
import type { FormattedMessage } from '../types';

describe('Whatsapp Store Utils', () => {
  afterEach(() => {
    cleanupTestDB();
  });

  describe('TEST_DB_PATH', () => {
    it('should be a valid path', () => {
      expect(TEST_DB_PATH).toBe('/tmp/test_message_db.json');
    });
  });

  describe('cleanupTestDB', () => {
    it('should remove the test database file if it exists', () => {
      // Create a dummy file
      fs.writeFileSync(TEST_DB_PATH, 'test');
      expect(fs.existsSync(TEST_DB_PATH)).toBe(true);

      cleanupTestDB();

      expect(fs.existsSync(TEST_DB_PATH)).toBe(false);
    });

    it('should not throw an error if the file does not exist', () => {
      expect(() => cleanupTestDB()).not.toThrow();
    });
  });

  describe('createMockMessage', () => {
    it('should create a mock message with default values', () => {
      const mockMessage = createMockMessage();

      expect(mockMessage).toEqual(expect.objectContaining({
        id: 'test-id',
        userId: 'test-user',
        chatId: 'test-chat',
        text: 'Test message',
        processed: false,
        meta: {
          fromMe: false,
        },
      }));

      expect(mockMessage.timestamp).toBeDefined();
      expect(typeof mockMessage.timestamp).toBe('number');
    });

    it('should override default values with provided overrides', () => {
      const overrides: Partial<FormattedMessage> = {
        id: 'custom-id',
        text: 'Custom message',
        processed: true,
      };

      const mockMessage = createMockMessage(overrides);

      expect(mockMessage).toEqual(expect.objectContaining({
        id: 'custom-id',
        userId: 'test-user',
        chatId: 'test-chat',
        text: 'Custom message',
        processed: true,
        meta: {
          fromMe: false,
        },
      }));
    });
  });
});
