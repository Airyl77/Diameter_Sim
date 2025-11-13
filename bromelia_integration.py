"""
Bromelia Integration Module for Gy Protocol

This module provides proper integration with the bromelia Diameter library,
including AVP creation, message building, and protocol handling.
"""

try:
    from bromelia import Diameter
    from bromelia.avps import *
    from bromelia.constants import *
    from bromelia.base import DiameterRequest, DiameterAnswer
    BROMELIA_AVAILABLE = True
except ImportError:
    BROMELIA_AVAILABLE = False


class BromeliaGyApplication:
    """
    Full Gy Diameter Application using bromelia library
    
    This class provides complete Diameter Credit-Control functionality
    with proper AVP handling and message creation.
    """
    
    def __init__(self, config):
        """
        Initialize Bromelia Gy Application
        
        Args:
            config: Configuration dictionary with:
                - host: Diameter host identity
                - realm: Diameter realm
                - ip: IP to bind (default: 0.0.0.0)
                - port: Port to listen (default: 3868)
        """
        if not BROMELIA_AVAILABLE:
            raise ImportError("Bromelia library is required. Install with: pip install bromelia")
        
        self.config = config
        self.stats = {
            'ccr_initial_received': 0,
            'ccr_update_received': 0,
            'ccr_terminate_received': 0,
            'ccr_event_received': 0,
            'cca_sent': 0,
            'errors': 0
        }
        
        # Create Diameter application
        self.app = Diameter(
            application_id=DIAMETER_APPLICATION_CREDIT_CONTROL,
            is_stateless=False
        )
        
        # Register message handlers
        self.app.add_handler(
            CREDIT_CONTROL_MESSAGE,
            self._handle_credit_control_request
        )
    
    def start(self, blocking=True):
        """
        Start the Diameter application
        
        Args:
            blocking: If True, runs in blocking mode
        """
        print(f"\n{'='*70}")
        print(f"Starting Gy Diameter Application with Bromelia")
        print(f"{'='*70}")
        print(f"Host Identity: {self.config['host']}")
        print(f"Realm: {self.config['realm']}")
        print(f"Listening on: {self.config.get('ip', '0.0.0.0')}:{self.config.get('port', 3868)}")
        print(f"{'='*70}\n")
        
        # Start the application
        self.app.listen(
            self.config.get('ip', '0.0.0.0'),
            self.config.get('port', 3868)
        )
        
        if blocking:
            print("✓ Server started successfully")
            print("✓ Press Ctrl+C to stop\n")
            try:
                self.app.run()
            except KeyboardInterrupt:
                print("\n\nShutting down...")
                self.stop()
    
    def stop(self):
        """Stop the application"""
        try:
            self.app.stop()
            print("Server stopped successfully.")
            self.print_statistics()
        except Exception as e:
            print(f"Error stopping server: {e}")
    
    def _handle_credit_control_request(self, request: DiameterRequest):
        """
        Handle incoming Credit-Control-Request
        
        Args:
            request: Bromelia DiameterRequest object
            
        Returns:
            DiameterAnswer object
        """
        try:
            # Extract session ID
            session_id = request.session_id_avp.data if hasattr(request, 'session_id_avp') else None
            
            # Extract CC-Request-Type
            cc_request_type = None
            if hasattr(request, 'cc_request_type_avp'):
                cc_request_type = request.cc_request_type_avp.data
            
            # Extract CC-Request-Number
            cc_request_number = None
            if hasattr(request, 'cc_request_number_avp'):
                cc_request_number = request.cc_request_number_avp.data
            
            # Update statistics based on request type
            if cc_request_type == CC_REQUEST_TYPE_INITIAL_REQUEST:
                self.stats['ccr_initial_received'] += 1
                print(f"[{self._get_timestamp()}] CCR Initial: Session={session_id}, Seq={cc_request_number}")
            elif cc_request_type == CC_REQUEST_TYPE_UPDATE_REQUEST:
                self.stats['ccr_update_received'] += 1
                print(f"[{self._get_timestamp()}] CCR Update: Session={session_id}, Seq={cc_request_number}")
            elif cc_request_type == CC_REQUEST_TYPE_TERMINATION_REQUEST:
                self.stats['ccr_terminate_received'] += 1
                print(f"[{self._get_timestamp()}] CCR Terminate: Session={session_id}, Seq={cc_request_number}")
            elif cc_request_type == CC_REQUEST_TYPE_EVENT_REQUEST:
                self.stats['ccr_event_received'] += 1
                print(f"[{self._get_timestamp()}] CCR Event: Session={session_id}, Seq={cc_request_number}")
            
            # Extract subscription information
            self._log_subscription_info(request)
            
            # Extract service units
            self._log_service_units(request)
            
            # Create and send answer
            answer = self._create_credit_control_answer(request)
            self.stats['cca_sent'] += 1
            
            print(f"[{self._get_timestamp()}] Sent CCA response\n")
            
            return answer
            
        except Exception as e:
            print(f"[{self._get_timestamp()}] Error handling CCR: {e}")
            self.stats['errors'] += 1
            return self._create_error_answer(request, DIAMETER_UNABLE_TO_COMPLY)
    
    def _create_credit_control_answer(self, request: DiameterRequest):
        """
        Create Credit-Control-Answer
        
        Args:
            request: Original CCR request
            
        Returns:
            DiameterAnswer with granted quota
        """
        # Create answer from request
        answer = request.to_answer()
        
        # Set Result-Code to SUCCESS
        answer.append_avp(ResultCodeAVP(DIAMETER_SUCCESS))
        
        # Get request type
        cc_request_type = None
        if hasattr(request, 'cc_request_type_avp'):
            cc_request_type = request.cc_request_type_avp.data
        
        # For INITIAL and UPDATE requests, grant quota
        if cc_request_type in [CC_REQUEST_TYPE_INITIAL_REQUEST, CC_REQUEST_TYPE_UPDATE_REQUEST]:
            # Grant 1 hour of time and 100MB of data
            granted_unit = GrantedServiceUnitAVP([
                CCTimeAVP(3600),  # 1 hour in seconds
                CCTotalOctetsAVP(104857600),  # 100 MB in bytes
            ])
            answer.append_avp(granted_unit)
            
            # Add validity time (1 hour)
            answer.append_avp(ValidityTimeAVP(3600))
            
            print(f"[{self._get_timestamp()}]   Granted: 1 hour, 100 MB")
        
        return answer
    
    def _create_error_answer(self, request: DiameterRequest, result_code: int):
        """
        Create error answer
        
        Args:
            request: Original request
            result_code: Diameter result code
            
        Returns:
            DiameterAnswer with error code
        """
        answer = request.to_answer()
        answer.append_avp(ResultCodeAVP(result_code))
        return answer
    
    def _log_subscription_info(self, request: DiameterRequest):
        """Log subscription information from request"""
        if hasattr(request, 'subscription_id_avp'):
            sub_id = request.subscription_id_avp
            if hasattr(sub_id, 'subscription_id_data_avp'):
                msisdn = sub_id.subscription_id_data_avp.data
                print(f"[{self._get_timestamp()}]   MSISDN: {msisdn}")
    
    def _log_service_units(self, request: DiameterRequest):
        """Log service units from request"""
        # Log requested units
        if hasattr(request, 'requested_service_unit_avp'):
            rsu = request.requested_service_unit_avp
            units = []
            if hasattr(rsu, 'cc_time_avp'):
                units.append(f"{rsu.cc_time_avp.data}s")
            if hasattr(rsu, 'cc_total_octets_avp'):
                mb = rsu.cc_total_octets_avp.data / 1024 / 1024
                units.append(f"{mb:.1f}MB")
            if units:
                print(f"[{self._get_timestamp()}]   Requested: {', '.join(units)}")
        
        # Log used units
        if hasattr(request, 'used_service_unit_avp'):
            usu = request.used_service_unit_avp
            units = []
            if hasattr(usu, 'cc_time_avp'):
                units.append(f"{usu.cc_time_avp.data}s")
            if hasattr(usu, 'cc_total_octets_avp'):
                mb = usu.cc_total_octets_avp.data / 1024 / 1024
                units.append(f"{mb:.1f}MB")
            if units:
                print(f"[{self._get_timestamp()}]   Used: {', '.join(units)}")
    
    def _get_timestamp(self):
        """Get formatted timestamp"""
        from datetime import datetime
        return datetime.now().strftime("%H:%M:%S")
    
    def print_statistics(self):
        """Print application statistics"""
        print("\n" + "="*70)
        print("Gy Diameter Application Statistics:")
        print("="*70)
        print(f"CCR Initial Received:    {self.stats['ccr_initial_received']}")
        print(f"CCR Update Received:     {self.stats['ccr_update_received']}")
        print(f"CCR Terminate Received:  {self.stats['ccr_terminate_received']}")
        print(f"CCR Event Received:      {self.stats['ccr_event_received']}")
        print(f"CCA Sent:                {self.stats['cca_sent']}")
        print(f"Errors:                  {self.stats['errors']}")
        print("="*70 + "\n")
    
    def get_statistics(self):
        """Get statistics dictionary"""
        return self.stats.copy()


def is_bromelia_available():
    """Check if bromelia is available"""
    return BROMELIA_AVAILABLE


def create_gy_application(config, use_bromelia=None):
    """
    Factory function to create Gy application
    
    Args:
        config: Configuration dictionary
        use_bromelia: Force bromelia usage (None=auto-detect, True=force, False=mock)
        
    Returns:
        BromeliaGyApplication or None if bromelia not available
    """
    if use_bromelia is None:
        use_bromelia = BROMELIA_AVAILABLE
    
    if use_bromelia and not BROMELIA_AVAILABLE:
        raise ImportError("Bromelia requested but not installed. Install with: pip install bromelia")
    
    if use_bromelia:
        return BromeliaGyApplication(config)
    else:
        return None  # Fall back to mock server

