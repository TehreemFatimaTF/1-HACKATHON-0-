"""
Specialized Analytics Agent for Platinum Tier
Handles metrics, reporting, and business intelligence
"""

from typing import Dict, List
from .base_agent import BaseAgent, AgentCapability
from datetime import datetime, timedelta
import json


class AnalyticsAgent(BaseAgent):
    """
    Specialized agent for analytics and reporting.
    Generates insights, metrics, and executive summaries.
    """

    def __init__(self, agent_id: str = None):
        super().__init__(
            agent_id=agent_id,
            name="AnalyticsAgent",
            specialization="analytics",
            capabilities=[
                AgentCapability.ANALYTICS,
                AgentCapability.COORDINATION
            ]
        )
        self.metrics_history = []
        self.reports_generated = []

    def _execute_task_impl(self, task: Dict) -> Dict:
        """
        Execute analytics tasks

        Args:
            task: Analytics task to execute

        Returns:
            Dict: Execution result
        """
        task_type = task.get("type", "")

        if task_type == "analytics_generate_report":
            return self._generate_report(task)
        elif task_type == "analytics_calculate_metrics":
            return self._calculate_metrics(task)
        elif task_type == "analytics_executive_summary":
            return self._generate_executive_summary(task)
        elif task_type == "analytics_roi":
            return self._calculate_roi(task)
        else:
            return {
                "success": False,
                "error": f"Unknown analytics task type: {task_type}"
            }

    def _generate_report(self, task: Dict) -> Dict:
        """Generate analytics report"""
        try:
            report_type = task.get("data", {}).get("report_type", "daily")
            data_source = task.get("data", {}).get("data_source", {})

            report = {
                "report_id": task.get("task_id"),
                "report_type": report_type,
                "generated_at": datetime.now().isoformat(),
                "metrics": self._extract_metrics(data_source),
                "insights": self._generate_insights(data_source),
                "recommendations": self._generate_recommendations(data_source)
            }

            self.reports_generated.append(report)

            return {
                "success": True,
                "message": f"{report_type.capitalize()} report generated",
                "report": report
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to generate report: {str(e)}"
            }

    def _calculate_metrics(self, task: Dict) -> Dict:
        """Calculate performance metrics"""
        try:
            data = task.get("data", {})
            metric_type = data.get("metric_type", "performance")

            metrics = {
                "metric_type": metric_type,
                "calculated_at": datetime.now().isoformat(),
                "values": {}
            }

            if metric_type == "performance":
                metrics["values"] = self._calculate_performance_metrics(data)
            elif metric_type == "efficiency":
                metrics["values"] = self._calculate_efficiency_metrics(data)
            elif metric_type == "cost":
                metrics["values"] = self._calculate_cost_metrics(data)

            self.metrics_history.append(metrics)

            return {
                "success": True,
                "message": f"{metric_type.capitalize()} metrics calculated",
                "metrics": metrics
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to calculate metrics: {str(e)}"
            }

    def _generate_executive_summary(self, task: Dict) -> Dict:
        """Generate executive summary"""
        try:
            data = task.get("data", {})
            period = data.get("period", "daily")

            # Aggregate data from all sources
            summary = {
                "period": period,
                "generated_at": datetime.now().isoformat(),
                "key_metrics": self._get_key_metrics(data),
                "highlights": self._get_highlights(data),
                "concerns": self._get_concerns(data),
                "action_items": self._get_action_items(data)
            }

            return {
                "success": True,
                "message": f"Executive summary for {period} generated",
                "summary": summary
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to generate executive summary: {str(e)}"
            }

    def _calculate_roi(self, task: Dict) -> Dict:
        """Calculate return on investment"""
        try:
            data = task.get("data", {})
            investment = data.get("investment", 0)
            returns = data.get("returns", 0)
            time_period = data.get("time_period", "monthly")

            if investment == 0:
                roi_percentage = 0
            else:
                roi_percentage = ((returns - investment) / investment) * 100

            roi_analysis = {
                "investment": investment,
                "returns": returns,
                "roi_percentage": round(roi_percentage, 2),
                "time_period": time_period,
                "calculated_at": datetime.now().isoformat(),
                "status": "positive" if roi_percentage > 0 else "negative"
            }

            return {
                "success": True,
                "message": f"ROI calculated: {roi_percentage:.2f}%",
                "roi_analysis": roi_analysis
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to calculate ROI: {str(e)}"
            }

    def _extract_metrics(self, data_source: Dict) -> Dict:
        """Extract metrics from data source"""
        return {
            "total_tasks": data_source.get("total_tasks", 0),
            "completed_tasks": data_source.get("completed_tasks", 0),
            "success_rate": data_source.get("success_rate", 0),
            "average_completion_time": data_source.get("avg_time", 0)
        }

    def _generate_insights(self, data_source: Dict) -> List[str]:
        """Generate insights from data"""
        insights = []

        success_rate = data_source.get("success_rate", 0)
        if success_rate > 90:
            insights.append("Excellent performance with >90% success rate")
        elif success_rate < 70:
            insights.append("Performance below target - investigation needed")

        total_tasks = data_source.get("total_tasks", 0)
        if total_tasks > 100:
            insights.append("High volume of tasks processed")

        return insights

    def _generate_recommendations(self, data_source: Dict) -> List[str]:
        """Generate recommendations based on data"""
        recommendations = []

        success_rate = data_source.get("success_rate", 0)
        if success_rate < 80:
            recommendations.append("Review failed tasks and improve error handling")

        avg_time = data_source.get("avg_time", 0)
        if avg_time > 300:  # 5 minutes
            recommendations.append("Optimize task execution time")

        return recommendations

    def _calculate_performance_metrics(self, data: Dict) -> Dict:
        """Calculate performance metrics"""
        return {
            "tasks_per_hour": data.get("tasks_completed", 0) / max(data.get("hours", 1), 1),
            "success_rate": data.get("success_rate", 0),
            "error_rate": 100 - data.get("success_rate", 0),
            "average_response_time": data.get("avg_response_time", 0)
        }

    def _calculate_efficiency_metrics(self, data: Dict) -> Dict:
        """Calculate efficiency metrics"""
        return {
            "automation_rate": data.get("automated_tasks", 0) / max(data.get("total_tasks", 1), 1) * 100,
            "time_saved_hours": data.get("time_saved", 0),
            "cost_per_task": data.get("total_cost", 0) / max(data.get("total_tasks", 1), 1)
        }

    def _calculate_cost_metrics(self, data: Dict) -> Dict:
        """Calculate cost metrics"""
        return {
            "total_cost": data.get("total_cost", 0),
            "cost_per_user": data.get("total_cost", 0) / max(data.get("users", 1), 1),
            "cost_savings": data.get("cost_savings", 0),
            "roi": data.get("roi", 0)
        }

    def _get_key_metrics(self, data: Dict) -> Dict:
        """Get key metrics for executive summary"""
        return {
            "total_tasks_completed": data.get("completed_tasks", 0),
            "success_rate": data.get("success_rate", 0),
            "time_saved_hours": data.get("time_saved", 0),
            "cost_savings": data.get("cost_savings", 0)
        }

    def _get_highlights(self, data: Dict) -> List[str]:
        """Get highlights for executive summary"""
        highlights = []

        if data.get("success_rate", 0) > 95:
            highlights.append("Exceptional performance with 95%+ success rate")

        if data.get("cost_savings", 0) > 10000:
            highlights.append(f"Significant cost savings: ${data.get('cost_savings', 0):,.2f}")

        return highlights

    def _get_concerns(self, data: Dict) -> List[str]:
        """Get concerns for executive summary"""
        concerns = []

        if data.get("error_rate", 0) > 10:
            concerns.append("Error rate above acceptable threshold")

        if data.get("pending_tasks", 0) > 50:
            concerns.append("High backlog of pending tasks")

        return concerns

    def _get_action_items(self, data: Dict) -> List[str]:
        """Get action items for executive summary"""
        action_items = []

        if data.get("failed_tasks", 0) > 5:
            action_items.append("Review and address failed tasks")

        if data.get("avg_response_time", 0) > 300:
            action_items.append("Optimize response time")

        return action_items

    def get_analytics_stats(self) -> Dict:
        """Get analytics agent statistics"""
        return {
            "reports_generated": len(self.reports_generated),
            "metrics_tracked": len(self.metrics_history),
            "recent_reports": self.reports_generated[-5:],
            "agent_metrics": self.metrics
        }
