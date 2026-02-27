def get_ai_suggestions(expenses_by_category, total_expense, budget_limit=0, current_month_spending=0):
    suggestions = []
    
    if total_expense == 0:
        return ["Start tracking your expenses by uploading a CSV!"]

    # Budget Awareness
    if budget_limit > 0:
        if current_month_spending > budget_limit:
            suggestions.append(f"⚠️ You have exceeded your monthly budget by ₹{current_month_spending - budget_limit:,.2f}. Try to cut down on discretionary spending.")
        elif current_month_spending > budget_limit * 0.9:
            suggestions.append("👀 You have reached 90% of your budget. Be careful with your next few purchases.")
        elif current_month_spending > 0:
            suggestions.append(f"⭐ You're doing great! You still have ₹{budget_limit - current_month_spending:,.2f} left in your budget.")

    # Calculate percentages
    percentages = {cat: (amt / total_expense) * 100 for cat, amt in expenses_by_category.items()}
    
    if percentages.get('Food', 0) > 30:
        suggestions.append("🍔 Your food spending is over 30% of your total expense. Consider eating out less or meal prepping.")
    
    if percentages.get('Entertainment', 0) > 20:
        suggestions.append("🎬 Leisure spending is high (20%+). You might want to review your active subscriptions.")
    
    if percentages.get('Rent', 0) > 40:
        suggestions.append("🏠 Rent is taking up more than 40% of your expenses. Consider looking for more affordable housing or sharing costs.")
    
    if total_expense < 10000 and budget_limit == 0: 
        suggestions.append("💰 Great job keeping your expenses low! Set a budget to track your saving goals better.")
    
    if not suggestions:
        suggestions.append("✅ Your spending looks balanced! Keep maintaining this healthy budget.")
        
    return suggestions
