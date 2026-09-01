import requests
import logging
from typing import Dict, Any, Optional
from config import config

logger = logging.getLogger(__name__)

class SMMPanelAPI:
    """SMM Panel API Client for SMMCPAN integration"""
    
    def __init__(self):
        self.api_key = config.SMMCPAN_API_KEY
        self.base_url = config.SMMCPAN_API_URL
        self.timeout = config.API_TIMEOUT
        
    def _make_request(self, method: str, params: Dict[str, Any]) -> Optional[Dict]:
        """Make API request to SMM panel"""
        try:
            params['api_key'] = self.api_key
            
            if method == 'GET':
                response = requests.get(
                    self.base_url,
                    params=params,
                    timeout=self.timeout
                )
            else:
                response = requests.post(
                    self.base_url,
                    data=params,
                    timeout=self.timeout
                )
            
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed: {e}")
            return None
    
    def get_services(self) -> Dict:
        """Get list of available services"""
        params = {
            'action': 'services'
        }
        return self._make_request('GET', params) or {}
    
    def get_service_info(self, service_id: int) -> Optional[Dict]:
        """Get specific service information"""
        params = {
            'action': 'service',
            'service': service_id
        }
        return self._make_request('GET', params)
    
    def place_order(self, service_id: int, link: str, quantity: int) -> Optional[Dict]:
        """Place new order"""
        params = {
            'action': 'add',
            'service': service_id,
            'link': link,
            'quantity': quantity
        }
        response = self._make_request('POST', params)
        
        if response and response.get('status') == 'success':
            logger.info(f"Order placed successfully: {response.get('order')}")
            return response
        else:
            logger.error(f"Failed to place order: {response}")
            return None
    
    def get_order_status(self, order_id: str) -> Optional[Dict]:
        """Get order status"""
        params = {
            'action': 'status',
            'order': order_id
        }
        return self._make_request('GET', params)
    
    def get_balance(self) -> Optional[float]:
        """Get account balance"""
        params = {
            'action': 'balance'
        }
        response = self._make_request('GET', params)
        
        if response:
            try:
                return float(response.get('balance', 0))
            except (ValueError, TypeError):
                return None
        return None
    
    def cancel_order(self, order_id: str) -> bool:
        """Cancel an order"""
        params = {
            'action': 'cancel',
            'order': order_id
        }
        response = self._make_request('POST', params)
        return response and response.get('status') == 'success'
    
    def refund_order(self, order_id: str) -> bool:
        """Request refund for an order"""
        params = {
            'action': 'refund',
            'order': order_id
        }
        response = self._make_request('POST', params)
        return response and response.get('status') == 'success'

# Create API instance
smm_api = SMMPanelAPI()
