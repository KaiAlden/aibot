from pydantic import BaseModel, Field


class ProductItem(BaseModel):
    id: int
    name: str
    category: str | None = None
    form: str | None = None
    description: str | None = None
    price: float | None = None
    weight: str | None = None
    image_url: str | None = None
    is_universal: bool = False
    constitutions: list[str] = Field(default_factory=list)
    ingredients: list[str] = Field(default_factory=list)


class ProductListResponse(BaseModel):
    items: list[ProductItem]
    total: int
    page: int
    size: int


class ProductCreateRequest(BaseModel):
    name: str
    category: str | None = None
    form: str | None = None
    description: str | None = None
    price: float | None = None
    weight: str | None = None
    image_url: str | None = None
    is_universal: bool = False
    constitutions: list[str] = Field(default_factory=list)
    ingredients: list[str] = Field(default_factory=list)


class ProductUpdateRequest(BaseModel):
    name: str | None = None
    category: str | None = None
    form: str | None = None
    description: str | None = None
    price: float | None = None
    weight: str | None = None
    image_url: str | None = None
    is_universal: bool | None = None
    constitutions: list[str] | None = None
    ingredients: list[str] | None = None


class ProductMutationResponse(BaseModel):
    item: ProductItem


class ProductImportIssueItem(BaseModel):
    sheet_name: str | None = None
    row_number: int | None = None
    field: str
    message: str
    value: str | None = None


class ProductImportResponse(BaseModel):
    parsed_count: int
    valid_count: int
    issue_count: int
    imported_count: int
    dry_run: bool
    replaced: bool
    unknown_constitutions: list[str] = Field(default_factory=list)
    issues: list[ProductImportIssueItem] = Field(default_factory=list)


class ProductImportMappingResponse(BaseModel):
    mapping: dict[str, str | list[str]]
    required_fields: list[str]


class ProductImportMappingUpdateRequest(BaseModel):
    mapping: dict[str, str | list[str]]


class ProductImportMappingUpdateResponse(BaseModel):
    mapping: dict[str, str | list[str]]
    saved: bool = True
