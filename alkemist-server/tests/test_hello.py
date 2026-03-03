tests/test_hello.py
import { test, expect } from '@jest/globals';

test('hello world', () => {
    expect(1 + 1).toBe(2);
});

pyproject.toml
[tool.poetry.dev-dependencies]
jest = "^27.0.0"

jest.config.js
module.exports = {
    testEnvironment: 'node',
    transform: {
        '^.+\\.jsx?$': 'babel-jest',
    },
};