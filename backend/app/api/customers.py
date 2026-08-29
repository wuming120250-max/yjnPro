from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas import CustomerDetail, CustomerListItem, CustomerListResponse, OrderItem
from app.services import customer_service

router = APIRouter(prefix="/api/customers", tags=["customers"])


@router.get("", response_model=CustomerListResponse)
def list_customers(
    keyword: str | None = Query(default=None),
    level: str | None = Query(default=None),
    tag: str | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=200),
    db: Session = Depends(get_db),
) -> CustomerListResponse:
    total, rows = customer_service.list_customers(
        db, keyword=keyword, level=level, tag=tag, page=page, page_size=page_size
    )
    items = [
        CustomerListItem.model_validate(customer_service.serialize_customer(row))
        for row in rows
    ]
    return CustomerListResponse(total=total, items=items)


@router.get("/{customer_id}", response_model=CustomerDetail)
def get_customer(customer_id: int, db: Session = Depends(get_db)) -> CustomerDetail:
    customer = customer_service.get_customer_detail(db, customer_id)
    if customer is None:
        raise HTTPException(status_code=404, detail="客户不存在")
    data = customer_service.serialize_customer(customer)
    orders = sorted(customer.orders, key=lambda item: item.order_date, reverse=True)
    data["orders"] = [OrderItem.model_validate(order) for order in orders]
    data["order_types"] = customer_service.get_order_types(db, customer_id)
    return CustomerDetail.model_validate(data)
