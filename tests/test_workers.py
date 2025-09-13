"""
Test file for workers functionality.
"""
import pytest
import asyncio
import sys
from pathlib import Path

# Add src to path for testing
sys.path.append(str(Path(__file__).parent.parent / "src"))

from src.workers.message_processor import MessageProcessorWorker
from src.workers.business_logic_worker import BusinessLogicWorker
from src.workers.notification_worker import NotificationWorker
from src.workers.worker_manager import WorkerManager


class TestMessageProcessor:
    """Test cases for MessageProcessorWorker."""
    
    @pytest.mark.asyncio
    async def test_message_processor_initialization(self):
        """Test worker initialization."""
        worker = MessageProcessorWorker()
        await worker.start()
        assert worker.is_running is True
        await worker.stop()
        assert worker.is_running is False
    
    @pytest.mark.asyncio
    async def test_command_processing(self):
        """Test command message processing."""
        worker = MessageProcessorWorker()
        await worker.start()
        
        message_data = {
            "message_id": 123,
            "text": "/start",
            "user_id": 456,
            "chat_id": 789
        }
        
        result = await worker.process(message_data)
        assert result["status"] == "success"
        assert result["type"] == "command"
        
        await worker.stop()


class TestBusinessLogicWorker:
    """Test cases for BusinessLogicWorker."""
    
    @pytest.mark.asyncio
    async def test_user_registration(self):
        """Test user registration logic."""
        worker = BusinessLogicWorker()
        await worker.start()
        
        request_data = {
            "operation": "user_registration",
            "user_id": 123,
            "params": {
                "name": "Test User",
                "email": "test@example.com",
                "age": 25
            }
        }
        
        result = await worker.process(request_data)
        assert result["status"] == "success"
        assert "User registered successfully" in result["message"]
        
        await worker.stop()
    
    @pytest.mark.asyncio
    async def test_invalid_user_age(self):
        """Test user registration with invalid age."""
        worker = BusinessLogicWorker()
        await worker.start()
        
        request_data = {
            "operation": "user_registration",
            "user_id": 123,
            "params": {
                "name": "Test User",
                "email": "test@example.com",
                "age": 16  # Below minimum age
            }
        }
        
        result = await worker.process(request_data)
        assert result["status"] == "error"
        assert "18 or older" in result["message"]
        
        await worker.stop()


class TestNotificationWorker:
    """Test cases for NotificationWorker."""
    
    @pytest.mark.asyncio
    async def test_welcome_notification(self):
        """Test welcome notification sending."""
        worker = NotificationWorker()
        await worker.start()
        
        notification_data = {
            "type": "welcome",
            "user_id": 123,
            "template_data": {
                "name": "Test User"
            }
        }
        
        result = await worker.process(notification_data)
        assert result["status"] == "success"
        assert "Welcome notification sent" in result["message"]
        
        await worker.stop()


class TestWorkerManager:
    """Test cases for WorkerManager."""
    
    @pytest.mark.asyncio
    async def test_worker_manager_initialization(self):
        """Test worker manager initialization."""
        manager = WorkerManager()
        await manager.start()
        
        status = manager.get_worker_status()
        assert "message_processor" in status
        assert "business_logic" in status
        assert "notification" in status
        
        for worker_name, worker_status in status.items():
            assert worker_status["is_running"] is True
        
        await manager.stop()
    
    @pytest.mark.asyncio
    async def test_message_processing_through_manager(self):
        """Test message processing through worker manager."""
        manager = WorkerManager()
        await manager.start()
        
        message_data = {
            "message_id": 123,
            "text": "Hello",
            "user_id": 456,
            "chat_id": 789
        }
        
        result = await manager.process_message(message_data)
        assert result["status"] == "success"
        
        await manager.stop()


if __name__ == "__main__":
    # Run a simple test
    async def run_simple_test():
        """Run a simple test to verify everything works."""
        print("Running simple worker test...")
        
        # Test worker manager
        manager = WorkerManager()
        await manager.start()
        
        # Test message processing
        message_data = {
            "message_id": 1,
            "text": "/start",
            "user_id": 123,
            "chat_id": 456
        }
        result = await manager.process_message(message_data)
        print(f"Message processing result: {result}")
        
        # Test business logic
        registration_data = {
            "operation": "user_registration",
            "user_id": 123,
            "params": {
                "name": "John Doe",
                "email": "john@example.com",
                "age": 25
            }
        }
        result = await manager.execute_business_logic(registration_data)
        print(f"Business logic result: {result}")
        
        # Test notification
        notification_data = {
            "type": "welcome",
            "user_id": 123,
            "template_data": {
                "name": "John Doe"
            }
        }
        result = await manager.send_notification(notification_data)
        print(f"Notification result: {result}")
        
        await manager.stop()
        print("Test completed successfully!")
    
    asyncio.run(run_simple_test())
