import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
from telegram.ext import ContextTypes
from database import SessionLocal, User, Order, Payment
from smm_api import smm_api
from config import config

logger = logging.getLogger(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Start command handler"""
    db = SessionLocal()
    user = db.query(User).filter(User.telegram_id == update.effective_user.id).first()
    
    if not user:
        user = User(
            telegram_id=update.effective_user.id,
            username=update.effective_user.username,
            first_name=update.effective_user.first_name,
            last_name=update.effective_user.last_name
        )
        db.add(user)
        db.commit()
    
    db.close()
    
    welcome_text = f"""
    👋 مرحباً بك في بوت SMM Panel

    أنا بوت متقدم لزيادة المتابعين والمشاهدات والتفاعلات على جميع منصات التواصل الاجتماعي.

    الخدمات المتاحة:
    ✅ متابعين تليجرام
    ✅ متابعين إنستغرام
    ✅ متابعين تيك توك
    ✅ وغيرها الكثير...

    اختر من القائمة أدناه للبدء:
    """
    
    keyboard = [
        ['🛒 طلب خدمة', '👤 حسابي'],
        ['💰 رصيدي', '📋 طلباتي'],
        ['❓ المساعدة', '⚙️ الإعدادات']
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=False)
    
    await update.message.reply_text(welcome_text, reply_markup=reply_markup)

async def services_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show available services"""
    services_text = "🛒 الخدمات المتاحة:\n\n"
    
    for service_key, service_info in config.AVAILABLE_SERVICES.items():
        services_text += f"• {service_info['name']}\n"
        services_text += f"  {service_info['description']}\n"
        services_text += f"  السعر: يتم حسابه حسب الكمية\n\n"
    
    keyboard = [[InlineKeyboardButton(text="🛍️ اطلب الآن", callback_data="order_new")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(services_text, reply_markup=reply_markup)

async def my_account(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show user account information"""
    db = SessionLocal()
    user = db.query(User).filter(User.telegram_id == update.effective_user.id).first()
    
    if user:
        account_text = f"""
        👤 معلومات الحساب:
        
        الاسم: {user.first_name} {user.last_name or ''}
        معرّف المستخدم: @{user.username or 'غير محدد'}
        الرصيد الحالي: ${user.balance:.2f}
        تاريخ الانضمام: {user.created_at.strftime('%Y-%m-%d %H:%M')}
        """
    else:
        account_text = "❌ لم يتم العثور على حسابك"
    
    db.close()
    await update.message.reply_text(account_text)

async def my_balance(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show user balance"""
    db = SessionLocal()
    user = db.query(User).filter(User.telegram_id == update.effective_user.id).first()
    
    if user:
        balance_text = f"""
        💰 رصيدك الحالي: ${user.balance:.2f}
        
        اختر عملية:
        """
        keyboard = [
            [InlineKeyboardButton("➕ إضافة رصيد", callback_data="add_balance")],
            [InlineKeyboardButton("📊 سجل الدفعات", callback_data="payment_history")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(balance_text, reply_markup=reply_markup)
    else:
        await update.message.reply_text("❌ لم يتم العثور على حسابك")
    
    db.close()

async def my_orders(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show user orders"""
    db = SessionLocal()
    user = db.query(User).filter(User.telegram_id == update.effective_user.id).first()
    
    if user:
        orders = db.query(Order).filter(Order.user_id == user.id).order_by(Order.created_at.desc()).limit(10).all()
        
        if orders:
            orders_text = "📋 آخر طلباتك:\n\n"
            for order in orders:
                status_emoji = {
                    'pending': '⏳',
                    'processing': '🔄',
                    'completed': '✅',
                    'failed': '❌'
                }.get(order.status, '❓')
                
                orders_text += f"{status_emoji} الطلب #{order.id}\n"
                orders_text += f"   الخدمة: {order.service_type}\n"
                orders_text += f"   الكمية: {order.quantity}\n"
                orders_text += f"   السعر: ${order.price:.2f}\n"
                orders_text += f"   التاريخ: {order.created_at.strftime('%Y-%m-%d %H:%M')}\n\n"
        else:
            orders_text = "📋 لم تقم بأي طلبات حتى الآن"
    else:
        orders_text = "❌ لم يتم العثور على حسابك"
    
    db.close()
    await update.message.reply_text(orders_text)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show help information"""
    help_text = """
    ❓ مساعدة وشروط الاستخدام:
    
    1️⃣ كيفية الطلب:
       - اختر الخدمة من القائمة
       - أدخل رابط حسابك أو قناتك
       - حدد الكمية المطلوبة
       - قم بالدفع
       - سيتم تسليم الخدمة في الحال
    
    2️⃣ طرق الدفع:
       - بطاقات الائتمان
       - محافظ رقمية
       - تحويل بنكي
    
    3️⃣ ضمان الخدمة:
       - جميع خدماتنا مضمونة 100%
       - إذا لم تكتمل الخدمة في 24 ساعة نرد لك الرصيد
    
    4️⃣ دعم العملاء:
       - متاح 24/7
       - اضغط على قسم المساعدة للتواصل معنا
    
    📞 للمزيد من المعلومات أو الشكاوى تواصل معنا
    """
    await update.message.reply_text(help_text)

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle button callbacks"""
    query = update.callback_query
    await query.answer()
    
    if query.data == "order_new":
        services_text = "اختر الخدمة التي تريد طلبها:\n\n"
        keyboard = []
        
        for service_key, service_info in config.AVAILABLE_SERVICES.items():
            keyboard.append([
                InlineKeyboardButton(
                    text=service_info['name'],
                    callback_data=f"service_{service_key}"
                )
            ])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(services_text, reply_markup=reply_markup)
    
    elif query.data == "add_balance":
        balance_text = """
        💳 اختر طريقة الدفع:
        """
        keyboard = [
            [InlineKeyboardButton("💳 بطاقة ائتمان", callback_data="pay_card")],
            [InlineKeyboardButton("📱 محفظة رقمية", callback_data="pay_wallet")],
            [InlineKeyboardButton("🏦 تحويل بنكي", callback_data="pay_bank")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(balance_text, reply_markup=reply_markup)

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle text messages"""
    text = update.message.text
    
    if text == "🛒 طلب خدمة":
        await services_command(update, context)
    elif text == "👤 حسابي":
        await my_account(update, context)
    elif text == "💰 رصيدي":
        await my_balance(update, context)
    elif text == "📋 طلباتي":
        await my_orders(update, context)
    elif text == "❓ المساعدة":
        await help_command(update, context)
    else:
        await update.message.reply_text("❌ أمر غير معروف. اختر من القائمة أعلاه")
