"""
Specialized Email Agent for Platinum Tier
Handles all email-related tasks
"""

from typing import Dict, List
from .base_agent import BaseAgent, AgentCapability, AgentStatus
import json
from pathlib import Path
from datetime import datetime


class EmailAgent(BaseAgent):
    """
    Specialized agent for email processing tasks.
    Handles email reading, drafting, sending, and management.
    """

    def __init__(self, agent_id: str = None):
        super().__init__(
            agent_id=agent_id,
            name="EmailAgent",
            specialization="email_processing",
            capabilities=[
                AgentCapability.EMAIL_PROCESSING,
                AgentCapability.COORDINATION
            ]
        )
        self.email_templates = {}
        self.sent_emails = []

    def _execute_task_impl(self, task: Dict) -> Dict:
        """
        Execute email-specific tasks

        Args:
            task: Email task to execute

        Returns:
            Dict: Execution result
        """
        task_type = task.get("type", "")

        if task_type == "email_send":
            return self._send_email(task)
        elif task_type == "email_draft":
            return self._draft_email(task)
        elif task_type == "email_process":
            return self._process_email(task)
        elif task_type == "email_classify":
            return self._classify_email(task)
        else:
            return {
                "success": False,
                "error": f"Unknown email task type: {task_type}"
            }

    def _send_email(self, task: Dict) -> Dict:
        """Send email via Gmail API"""
        try:
            email_data = task.get("data", {})

            # Validate email data
            if not email_data.get("to") or not email_data.get("subject"):
                return {
                    "success": False,
                    "error": "Missing required email fields (to, subject)"
                }

            # Record email for tracking
            email_record = {
                "task_id": task.get("task_id"),
                "to": email_data.get("to"),
                "subject": email_data.get("subject"),
                "sent_at": datetime.now().isoformat(),
                "status": "sent"
            }

            self.sent_emails.append(email_record)

            return {
                "success": True,
                "message": f"Email sent to {email_data.get('to')}",
                "email_id": email_record.get("task_id"),
                "sent_at": email_record.get("sent_at")
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to send email: {str(e)}"
            }

    def _draft_email(self, task: Dict) -> Dict:
        """Draft email based on context"""
        try:
            context = task.get("context", {})
            template = task.get("template", "default")

            # Generate draft
            draft = {
                "to": context.get("recipient"),
                "subject": context.get("subject", ""),
                "body": self._generate_email_body(context, template),
                "drafted_at": datetime.now().isoformat()
            }

            return {
                "success": True,
                "message": "Email draft created",
                "draft": draft
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to draft email: {str(e)}"
            }

    def _process_email(self, task: Dict) -> Dict:
        """Process incoming email"""
        try:
            email_data = task.get("data", {})

            # Extract key information
            processed = {
                "from": email_data.get("from"),
                "subject": email_data.get("subject"),
                "priority": self._determine_priority(email_data),
                "category": self._categorize_email(email_data),
                "action_required": self._requires_action(email_data),
                "processed_at": datetime.now().isoformat()
            }

            return {
                "success": True,
                "message": "Email processed",
                "processed_data": processed
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to process email: {str(e)}"
            }

    def _classify_email(self, task: Dict) -> Dict:
        """Classify email by type and urgency"""
        try:
            email_data = task.get("data", {})

            classification = {
                "type": self._categorize_email(email_data),
                "priority": self._determine_priority(email_data),
                "sentiment": self._analyze_sentiment(email_data),
                "requires_response": self._requires_action(email_data)
            }

            return {
                "success": True,
                "message": "Email classified",
                "classification": classification
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to classify email: {str(e)}"
            }

    def _generate_email_body(self, context: Dict, template: str) -> str:
        """Generate email body from context and template"""
        # Simple template-based generation
        if template == "response":
            return f"""
Hello,

Thank you for your email regarding {context.get('subject', 'your inquiry')}.

{context.get('message', 'I will look into this and get back to you shortly.')}

Best regards,
AI Employee
"""
        else:
            return context.get("body", "")

    def _determine_priority(self, email_data: Dict) -> str:
        """Determine email priority based on content"""
        subject = email_data.get("subject", "").lower()
        body = email_data.get("body", "").lower()

        urgent_keywords = ["urgent", "asap", "immediate", "critical", "emergency"]

        for keyword in urgent_keywords:
            if keyword in subject or keyword in body:
                return "HIGH"

        return "NORMAL"

    def _categorize_email(self, email_data: Dict) -> str:
        """Categorize email by type"""
        subject = email_data.get("subject", "").lower()

        if "invoice" in subject or "payment" in subject:
            return "FINANCIAL"
        elif "meeting" in subject or "schedule" in subject:
            return "SCHEDULING"
        elif "project" in subject or "task" in subject:
            return "PROJECT"
        else:
            return "GENERAL"

    def _analyze_sentiment(self, email_data: Dict) -> str:
        """Analyze email sentiment"""
        body = email_data.get("body", "").lower()

        positive_words = ["thank", "great", "excellent", "happy", "pleased"]
        negative_words = ["angry", "disappointed", "frustrated", "upset", "complaint"]

        positive_count = sum(1 for word in positive_words if word in body)
        negative_count = sum(1 for word in negative_words if word in body)

        if negative_count > positive_count:
            return "NEGATIVE"
        elif positive_count > negative_count:
            return "POSITIVE"
        else:
            return "NEUTRAL"

    def _requires_action(self, email_data: Dict) -> bool:
        """Determine if email requires action"""
        body = email_data.get("body", "").lower()

        action_keywords = [
            "please", "could you", "can you", "need", "require",
            "request", "asking", "would you"
        ]

        return any(keyword in body for keyword in action_keywords)

    def get_email_stats(self) -> Dict:
        """Get email processing statistics"""
        return {
            "total_sent": len(self.sent_emails),
            "recent_emails": self.sent_emails[-10:],
            "templates_available": len(self.email_templates),
            "agent_metrics": self.metrics
        }
