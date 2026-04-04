from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Sum, Count, Q
from django.db.models.functions import TruncMonth, TruncWeek
from ..models import FinancialRecord
from ..permissions import IsAnalystOrAbove
import datetime


class DashboardSummaryView(APIView):
    """
    Returns overall financial summary.
    Access: analyst, admin
    """
    permission_classes = [IsAnalystOrAbove]

    def get(self, request):
        qs = FinancialRecord.objects.filter(is_deleted=False)

        total_income  = qs.filter(entry_type='income').aggregate(
            total=Sum('amount'))['total'] or 0
        total_expense = qs.filter(entry_type='expense').aggregate(
            total=Sum('amount'))['total'] or 0
        net_balance   = total_income - total_expense

        # Category-wise breakdown
        category_totals = list(
            qs.values('category', 'entry_type')
              .annotate(total=Sum('amount'))
              .order_by('category')
        )

        # Recent 5 records
        recent = FinancialRecord.objects.filter(is_deleted=False) \
                    .select_related('created_by') \
                    .order_by('-date', '-created_at')[:5]
        recent_data = [
            {
                "id":          r.id,
                "amount":      str(r.amount),
                "entry_type":  r.entry_type,
                "category":    r.category,
                "date":        str(r.date),
                "description": r.description,
            }
            for r in recent
        ]

        return Response({
            "total_income":    str(total_income),
            "total_expense":   str(total_expense),
            "net_balance":     str(net_balance),
            "category_totals": category_totals,
            "recent_activity": recent_data,
        })


class MonthlyTrendView(APIView):
    """
    Monthly income vs expense trend for the past N months.
    Access: analyst, admin
    """
    permission_classes = [IsAnalystOrAbove]

    def get(self, request):
        months = int(request.query_params.get('months', 6))
        if not (1 <= months <= 24):
            return Response(
                {"error": "months must be between 1 and 24."},
                status=status.HTTP_400_BAD_REQUEST
            )

        since = datetime.date.today() - datetime.timedelta(days=months * 30)
        qs = FinancialRecord.objects.filter(is_deleted=False, date__gte=since)

        income_trend = list(
            qs.filter(entry_type='income')
              .annotate(month=TruncMonth('date'))
              .values('month')
              .annotate(total=Sum('amount'))
              .order_by('month')
        )
        expense_trend = list(
            qs.filter(entry_type='expense')
              .annotate(month=TruncMonth('date'))
              .values('month')
              .annotate(total=Sum('amount'))
              .order_by('month')
        )

        return Response({
            "income_trend":  income_trend,
            "expense_trend": expense_trend,
        })


class WeeklyTrendView(APIView):
    """
    Weekly trend for the past N weeks.
    Access: analyst, admin
    """
    permission_classes = [IsAnalystOrAbove]

    def get(self, request):
        weeks = int(request.query_params.get('weeks', 8))
        if not (1 <= weeks <= 52):
            return Response(
                {"error": "weeks must be between 1 and 52."},
                status=status.HTTP_400_BAD_REQUEST
            )

        since = datetime.date.today() - datetime.timedelta(weeks=weeks)
        qs = FinancialRecord.objects.filter(is_deleted=False, date__gte=since)

        trend = list(
            qs.annotate(week=TruncWeek('date'))
              .values('week', 'entry_type')
              .annotate(total=Sum('amount'))
              .order_by('week')
        )
        return Response({"weekly_trend": trend})