from django.contrib.auth.decorators import permission_required
from django.shortcuts import render, get_object_or_404, redirect
from juntagrico_custom_sub.models import (
    SubscriptionContent, SubscriptionContentFutureItem, SubscriptionSizeMandatoryProducts, Product,
    SubscriptionContentItem
    )
from juntagrico.models import Subscription
from juntagrico.views import get_menu_dict
from juntagrico.util.management_list import get_changedate
from juntagrico.util import return_to_previous_location
from juntagrico.dao.subscriptiondao import SubscriptionDao
from juntagrico.util.views_admin import subscription_management_list
from juntagrico_custom_sub.util.sub_content import new_content_valid, calculate_future_size, calculate_current_size
from juntagrico.decorators import create_subscription_session, primary_member_of_subscription
import logging

logger = logging.getLogger(__name__)


@primary_member_of_subscription
def subscription_content_edit(request, subscription_id=None):
    returnValues = dict()
    # subscription_id cannot be none --> route not defined
    # member = request.user.member
    # if subscription_id is None:
    #     subscription = member.subscription
    # else:
    subscription = get_object_or_404(Subscription, id=subscription_id)
    # subscription content should always exists in this view --> no try, exist?
    try:
        subContent = SubscriptionContent.objects.get(subscription=subscription)
    except SubscriptionContent.DoesNotExist:
        subContent = SubscriptionContent.objects.create(subscription=subscription)
        subContent.save()
        for type in subscription.future_types.all():
            for mandatoryProd in SubscriptionSizeMandatoryProducts.objects.filter(subscription_size=type.size):
                subItem = SubscriptionContentFutureItem.objects.create(
                    subscription_content=subContent,
                    product=mandatoryProd.product,
                    amount=mandatoryProd.amount
                    )
                subItem.save()
    products = Product.objects.all().order_by('user_editable')
    if "saveContent" in request.POST:
        valid, error = new_content_valid(subscription, request, products)
        if valid:
            for product in products:
                subItem, p = SubscriptionContentFutureItem.objects.get_or_create(
                    product=product,
                    subscription_content=subContent,
                    defaults={'amount': 0, 'product': product, 'subscription_content': subContent}
                    )
                subItem.amount = request.POST.get("amount"+str(product.id), 0)
                subItem.save()
            returnValues['saved'] = True
        else:
            returnValues['error'] = error
    subs_sizes = count_subs_sizes(subscription.future_types.all())
    for prod in products:
        sub_item = SubscriptionContentFutureItem.objects.filter(
            subscription_content=subContent.id, product=prod
            ).first()
        chosen_amount = 0 if not sub_item else sub_item.amount
        min_amount = determine_min_amount(prod, subs_sizes)
        prod.min_amount = min(min_amount, chosen_amount)
        prod.amount_in_subscription = max(chosen_amount, min_amount)

    returnValues['subscription'] = subscription
    returnValues['products'] = products
    returnValues['subscription_size'] = int(calculate_current_size(subscription))
    returnValues['future_subscription_size'] = int(calculate_future_size(subscription))
    return render(request, 'cs/subscription_content_edit.html', returnValues)


@create_subscription_session
def custom_sub_initial_select(request, cs_session):
    if request.method == 'POST':
        # create dict with subscription type -> selected amount
        custom_prod = selected_custom_products(request.POST)
        cs_session.custom_prod = custom_prod
        return redirect(cs_session.next_page())
    products = Product.objects.all().order_by('user_editable')
    subs_sizes = {t.size: a for t, a in cs_session.subscriptions.items() if a > 0}
    for p in products:
        p.min_amount = determine_min_amount(p, subs_sizes)
        p.amount_in_subscription = p.min_amount

    returnValues = {}
    returnValues['products'] = products
    returnValues['subscription_size'] = int(cs_session.subscription_size())
    returnValues['future_subscription_size'] = int(cs_session.subscription_size())
    return render(request, 'cs/subscription_content_edit.html', returnValues)


def add_products_to_subscription(subscription_id, custom_products):
    """
    adds custom products to the subscription with the given id.
    custom_prodducts is a dictionary with the product object as keys and their
    amount as value.
    """
    content = SubscriptionContent(subscription_id=subscription_id)
    content.save()
    selected_items = {
        p: a for p, a in custom_products.items() if a != 0
        }
    for prod, amount in selected_items.items():
        item = SubscriptionContentItem(
            amount=amount,
            product_id=prod.id,
            subscription_content_id=content.id
            )
        item.save()


def determine_min_amount(product, subs_sizes):
    '''
    Given a product and a dictionary of subscription sizes, return the minimum (mandatory) amount.
    Allows for situations where a product can be mandatory for more than one size.
    Example of subs_sizes: {size_1: amount_1, size_2: amount_2, etc...}
    '''
    min_amount = 0
    for size, count in subs_sizes.items():
        mand_prod = SubscriptionSizeMandatoryProducts.objects.filter(product=product, subscription_size=size).first()
        if mand_prod:
            min_amount += mand_prod.amount * count
    return min_amount


def count_subs_sizes(subs_types):
    rv = {}
    for st in subs_types:
        if st.size.id not in rv:
            rv[st.size.id] = 1
        else:
            rv[st.size.id] += 1
    return rv


def selected_custom_products(post_data):
    return {
        prod: int(
            post_data.get(f'amount{prod.id}', 0)
        ) for prod in Product.objects.all()
    }


@permission_required('juntagrico.is_operations_group')
def contentchangelist(request, subscription_id=None):
    render_dict = get_menu_dict(request)
    render_dict.update(get_changedate(request))
    changedlist = []
    subscriptions_list = SubscriptionDao.all_active_subscritions()
    for subscription in subscriptions_list:
        if subscription.content.content_changed:
            changedlist.append(subscription)
    return subscription_management_list(changedlist, render_dict, 'cs/contentchangelist.html', request)


@permission_required('juntagrico.is_operations_group')
def activate_future_content(request, subscription_id):
    subscription = get_object_or_404(Subscription, id=subscription_id)
    for content in subscription.content.products.all():
        content.delete()
    for content in subscription.content.future_products.all():
        SubscriptionContentItem.objects.create(
            subscription_content=subscription.content, amount=content.amount, product=content.product
            )
    return return_to_previous_location(request)
