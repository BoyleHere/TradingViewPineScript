import logging
import asyncio
import platform
from typing import Dict, List, Any
from datetime import datetime

# Platform-specific imports
if platform.system() == "Windows":
    try:
        import winsound
        SOUND_AVAILABLE = True
    except ImportError:
        SOUND_AVAILABLE = False
else:
    SOUND_AVAILABLE = False

try:
    from telegram import Bot
    TELEGRAM_AVAILABLE = True
except ImportError:
    TELEGRAM_AVAILABLE = False

class AlertManager:
    """Manages different types of alerts (console, telegram, sound)"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.alert_history = []
        
        # Initialize Telegram bot if available and configured
        self.telegram_bot = None
        if (TELEGRAM_AVAILABLE and 
            config.get('enable_telegram_alerts', False) and 
            config.get('telegram_bot_token') and 
            config.get('telegram_bot_token') != 'YOUR_BOT_TOKEN_HERE'):
            
            try:
                self.telegram_bot = Bot(token=config['telegram_bot_token'])
                self.telegram_chat_id = config.get('telegram_chat_id')
                self.logger.info("Telegram bot initialized successfully")
            except Exception as e:
                self.logger.error(f"Failed to initialize Telegram bot: {str(e)}")
                self.telegram_bot = None
        
        self.enable_console_alerts = config.get('enable_console_alerts', True)
        self.enable_sound_alerts = config.get('enable_sound_alerts', True)
        
        # Alert cooldown to prevent spam (in seconds)
        self.alert_cooldown = 60
        self.last_alert_time = {}
        
    def send_alert(self, alert_data: Dict[str, Any]):
        """Send alert through all configured channels"""
        # Create alert key for cooldown
        alert_key = f"{alert_data['symbol']}_{alert_data['timeframe']}_{alert_data['type']}_{alert_data['direction']}"
        
        # Check cooldown
        current_time = datetime.now()
        if (alert_key in self.last_alert_time and 
            (current_time - self.last_alert_time[alert_key]).total_seconds() < self.alert_cooldown):
            return
        
        self.last_alert_time[alert_key] = current_time
        
        # Format message
        message = self._format_alert_message(alert_data)
        
        # Store in history
        self.alert_history.append({
            'timestamp': current_time,
            'message': message,
            'data': alert_data
        })
        
        # Send through all channels
        if self.enable_console_alerts:
            self._send_console_alert(message)
        
        if self.enable_sound_alerts:
            self._send_sound_alert(alert_data['direction'])
        
        if self.telegram_bot and self.telegram_chat_id:
            self._send_telegram_alert(message)
    
    def _format_alert_message(self, alert_data: Dict[str, Any]) -> str:
        """Format alert message"""
        emoji = "🔥" if alert_data['type'] == 'FVG' else "🔄"
        direction_emoji = "🟢" if alert_data['direction'] == 'Bullish' else "🔴"
        
        message = f"{emoji} {alert_data['type']} Alert! {direction_emoji}\n"
        message += f"Symbol: {alert_data['symbol']}\n"
        message += f"Timeframe: {alert_data['timeframe']}\n"
        message += f"Direction: {alert_data['direction']}\n"
        
        if 'gap_size' in alert_data:
            message += f"Gap Size: {alert_data['gap_size']:.4f}\n"
        
        if 'gap_percentage' in alert_data:
            message += f"Gap %: {alert_data['gap_percentage']:.2f}%\n"
        
        if 'price' in alert_data:
            message += f"Price: ${alert_data['price']:.2f}\n"
        
        message += f"Time: {alert_data['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}"
        
        return message
    
    def _send_console_alert(self, message: str):
        """Send alert to console"""
        print(f"\n{'='*60}")
        print("🚨 TRADING ALERT 🚨")
        print(f"{'='*60}")
        print(message)
        print(f"{'='*60}\n")
        
        # Also log it
        self.logger.info(f"ALERT: {message}")
    
    def _send_sound_alert(self, direction: str):
        """Send sound alert"""
        try:
            if SOUND_AVAILABLE:
                # Different sounds for different directions
                if direction == 'Bullish':
                    winsound.Beep(1000, 500)  # High pitch for bullish
                else:
                    winsound.Beep(500, 500)   # Low pitch for bearish
            else:
                # For Linux/Mac - use system bell
                print('\a')
        except Exception as e:
            self.logger.warning(f"Could not play sound alert: {str(e)}")
    
    def _send_telegram_alert(self, message: str):
        """Send alert via Telegram"""
        try:
            asyncio.run(self.telegram_bot.send_message(
                chat_id=self.telegram_chat_id,
                text=message,
                parse_mode='HTML'
            ))
            self.logger.info("Telegram alert sent successfully")
        except Exception as e:
            self.logger.error(f"Failed to send Telegram alert: {str(e)}")
    
    def send_fvg_alert(self, symbol: str, timeframe: str, fvg_data: Dict):
        """Send FVG-specific alert"""
        alert_data = {
            'symbol': symbol,
            'timeframe': timeframe,
            'type': 'FVG',
            'direction': fvg_data['direction'],
            'gap_size': fvg_data['gap_size'],
            'gap_percentage': fvg_data['gap_percentage'],
            'price': fvg_data['price_at_detection'],
            'timestamp': fvg_data['timestamp']
        }
        self.send_alert(alert_data)
    
    def send_ifvg_alert(self, symbol: str, timeframe: str, ifvg_data: Dict):
        """Send iFVG-specific alert"""
        alert_data = {
            'symbol': symbol,
            'timeframe': timeframe,
            'type': 'iFVG',
            'direction': ifvg_data['direction'],
            'fill_percentage': ifvg_data['fill_percentage'],
            'price': ifvg_data['fill_price'],
            'timestamp': ifvg_data['timestamp']
        }
        self.send_alert(alert_data)
    
    def test_alerts(self):
        """Test all configured alert channels"""
        test_alert_data = {
            'symbol': 'TEST',
            'timeframe': '5m',
            'type': 'FVG',
            'direction': 'Bullish',
            'gap_size': 1.25,
            'gap_percentage': 0.85,
            'price': 150.00,
            'timestamp': datetime.now()
        }
        
        print("Testing alert system...")
        self.send_alert(test_alert_data)
        print("Alert test completed!")
    
    def get_alert_history(self, limit: int = 50) -> List[Dict]:
        """Get recent alert history"""
        return self.alert_history[-limit:]
    
    def clear_alert_history(self):
        """Clear alert history"""
        self.alert_history.clear()
        self.logger.info("Alert history cleared")
    
    def get_alert_stats(self) -> Dict:
        """Get alert statistics"""
        if not self.alert_history:
            return {
                'total_alerts': 0,
                'fvg_alerts': 0,
                'ifvg_alerts': 0,
                'bullish_alerts': 0,
                'bearish_alerts': 0
            }
        
        total = len(self.alert_history)
        fvg_count = sum(1 for alert in self.alert_history if alert['data']['type'] == 'FVG')
        ifvg_count = sum(1 for alert in self.alert_history if alert['data']['type'] == 'iFVG')
        bullish_count = sum(1 for alert in self.alert_history if alert['data']['direction'] == 'Bullish')
        bearish_count = sum(1 for alert in self.alert_history if alert['data']['direction'] == 'Bearish')
        
        return {
            'total_alerts': total,
            'fvg_alerts': fvg_count,
            'ifvg_alerts': ifvg_count,
            'bullish_alerts': bullish_count,
            'bearish_alerts': bearish_count
        }
