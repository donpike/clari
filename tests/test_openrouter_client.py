import pytest
import os
from src.api.openrouter_client import OpenRouterClient
from unittest.mock import patch, MagicMock
import requests

@pytest.fixture
def mock_config():
    return {
        'openrouter': {
            'default_model': 'claude-3-5-sonnet',
            'temperature': 0.7,
            'max_tokens': 2000
        }
    }

@pytest.fixture
def client(mock_config):
    with patch.dict('os.environ', {'OPENROUTER_API_KEY': 'test_key'}):
        return OpenRouterClient(mock_config)

def test_initialization_without_api_key(mock_config):
    """Test that client raises error when API key is missing"""
    with patch.dict('os.environ', {}, clear=True):
        with patch('dotenv.load_dotenv', return_value=None):
            with patch('os.getenv', return_value=None):
                with pytest.raises(ValueError, match="API key not found"):
                    OpenRouterClient(mock_config)

def test_create_prompt(client):
    """Test prompt creation with different inputs"""
    test_cases = [
        ("def hello(): pass", "Improve this function"),
        ("", "Analyze empty code"),
        ("a" * 1000, "Analyze long code"),
    ]
    
    for code, task in test_cases:
        messages = client.create_prompt(code, task)
        assert len(messages) == 2
        assert messages[0]['role'] == 'system'
        assert messages[1]['role'] == 'user'
        assert 'python' in messages[1]['content'].lower()

@pytest.mark.asyncio
async def test_analyze_code_success(client):
    """Test successful code analysis"""
    mock_response = {
        'choices': [{'message': {'content': 'Suggested improvements...'}}],
        'model': 'claude-3-5-sonnet',
        'usage': {'total_tokens': 100}
    }
    
    with patch.object(client, '_make_api_request') as mock_request:
        mock_request.return_value = mock_response
        result = await client.analyze_code("def test(): pass")
        assert 'suggestions' in result

@pytest.mark.asyncio
async def test_analyze_code_api_error(client):
    """Test handling of API errors"""
    with patch.object(client, '_make_api_request') as mock_request:
        mock_request.side_effect = requests.exceptions.RequestException("API Error")
        
        with pytest.raises(requests.exceptions.RequestException):
            await client.analyze_code("def test(): pass")

@pytest.mark.asyncio
async def test_analyze_code_invalid_response(client):
    """Test handling of invalid API responses"""
    invalid_responses = [
        {'choices': []},
        {'choices': [{}]},
        {'choices': [{'message': {}}]},
        {}
    ]
    
    for invalid_response in invalid_responses:
        with patch.object(client, '_make_api_request') as mock_request:
            mock_request.return_value = invalid_response
            with pytest.raises(ValueError, match="Unexpected API response format"):
                await client.analyze_code("def test(): pass")

@pytest.mark.asyncio
async def test_make_api_request(client):
    """Test API request formation"""
    test_messages = [{"role": "user", "content": "test"}]
    
    with patch('requests.post') as mock_post:
        mock_post.return_value.json.return_value = {"test": "response"}
        mock_post.return_value.raise_for_status = MagicMock()
        
        await client._make_api_request(test_messages)
        
        # Verify the API call
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        
        # Check headers
        assert 'Authorization' in call_args[1]['headers']
        assert call_args[1]['headers']['Authorization'] == 'Bearer test_key'
        
        # Check request body
        assert 'model' in call_args[1]['json']
        assert 'temperature' in call_args[1]['json']
        assert 'max_tokens' in call_args[1]['json']
        assert call_args[1]['json']['messages'] == test_messages

def test_parse_response(client):
    """Test response parsing with different response formats"""
    # Test valid response
    valid_response = {
        'choices': [{'message': {'content': 'test'}}],
        'model': 'test-model',
        'usage': {'total_tokens': 10}
    }
    result = client._parse_response(valid_response)
    assert result['suggestions'] == 'test'
    
    # Test invalid responses
    invalid_responses = [
        {'choices': []},
        {'choices': [{}]},
        {'choices': [{'message': {}}]},
        {}
    ]
    
    for invalid_response in invalid_responses:
        with pytest.raises(ValueError):
            client._parse_response(invalid_response) 