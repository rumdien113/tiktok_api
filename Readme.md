'''
git clone 
'''

'''
cd tiktok_api
'''

tạo file .env 
'''
.env
'''

'''
docker compsoe up -d
'''

Truy cập localhost:8000/swagger/ để xem api document

# Tiktokdb

## Bảng user

```sql
CREATE TABLE "user" (
    id UUID PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    firstname VARCHAR(50),
    lastname VARCHAR(50),
    birthdate DATE,
    phone VARCHAR(20),
    gender VARCHAR(10),
    avatar TEXT,
    bio TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,  -- Thêm trường này
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP   -- Thêm trường này
);
```

## Bảng post

```sql
CREATE TABLE "post" (
    id UUID PRIMARY KEY,
    user_id UUID NOT NULL,           -- Đổi tên từ id_user
    media TEXT,
    description TEXT,
    created_at TIMESTAMP NOT NULL,   -- Đổi tên từ createAt
    updated_at TIMESTAMP,            -- Thêm trường này
    FOREIGN KEY (user_id) REFERENCES "user"(id) ON DELETE CASCADE
);
```

## Bảng like

```sql
CREATE TABLE "like" (
    id UUID PRIMARY KEY,
    user_id UUID NOT NULL,           -- Đổi tên từ id_user
    target_id UUID NOT NULL,         -- Đổi tên từ id_target
    target_type VARCHAR(20) NOT NULL, -- Giới hạn độ dài
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,  -- Thêm trường này
    FOREIGN KEY (user_id) REFERENCES "user"(id) ON DELETE CASCADE,
    UNIQUE(user_id, target_id, target_type)  -- Thêm ràng buộc unique
);
```

## Bảng share

```sql
CREATE TABLE "share" (
    id UUID PRIMARY KEY,
    user_id UUID NOT NULL,           -- Đổi tên từ id_user
    post_id UUID NOT NULL,           -- Đổi tên từ id_post
    created_at TIMESTAMP NOT NULL,   -- Đổi tên từ createAt
    FOREIGN KEY (user_id) REFERENCES "user"(id) ON DELETE CASCADE,
    FOREIGN KEY (post_id) REFERENCES "post"(id) ON DELETE CASCADE
);
```

## Bảng comment

```sql
CREATE TABLE "comment" (
    id UUID PRIMARY KEY,
    post_id UUID NOT NULL,           -- Đổi tên từ id_post
    user_id UUID NOT NULL,           -- Đổi tên từ id_user
    parent_comment_id UUID,
    content TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL,   -- Đổi tên từ createAt
    updated_at TIMESTAMP,            -- Đổi tên từ updateAt
    FOREIGN KEY (post_id) REFERENCES "post"(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES "user"(id) ON DELETE CASCADE,
    FOREIGN KEY (parent_comment_id) REFERENCES "comment"(id) ON DELETE SET NULL
);
```

## Bảng follow

```sql
CREATE TABLE "follow" (
    id UUID PRIMARY KEY,
    follower_id UUID NOT NULL,
    followed_id UUID NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,  -- Thêm trường này
    FOREIGN KEY (follower_id) REFERENCES "user"(id) ON DELETE CASCADE,
    FOREIGN KEY (followed_id) REFERENCES "user"(id) ON DELETE CASCADE,
    UNIQUE(follower_id, followed_id)  -- Thêm ràng buộc unique
);
```

## Bảng tag

```sql
CREATE TABLE "tag" (
    id UUID PRIMARY KEY,
    name VARCHAR(50) UNIQUE NOT NULL  -- Thay đổi từ text sang VARCHAR có giới hạn
);
```

## Bảng post_tag

```sql
CREATE TABLE "post_tag" (
    id UUID PRIMARY KEY,
    post_id UUID NOT NULL,           -- Đổi tên từ id_post
    tag_id UUID NOT NULL,            -- Đổi tên từ id_tag
    FOREIGN KEY (post_id) REFERENCES "post"(id) ON DELETE CASCADE,
    FOREIGN KEY (tag_id) REFERENCES "tag"(id) ON DELETE CASCADE,
    UNIQUE(post_id, tag_id)  -- Thêm ràng buộc unique
);
```

## Bảng report

```sql
CREATE TABLE "report" (
    id UUID PRIMARY KEY,
    target_id UUID NOT NULL,         -- Đổi tên từ id_target
    target_type VARCHAR(20) NOT NULL,
    user_id UUID NOT NULL,           -- Thêm trường này
    reason VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,  -- Thêm trường này
    status VARCHAR(20) DEFAULT 'pending',  -- Thêm trường này
    FOREIGN KEY (user_id) REFERENCES "user"(id) ON DELETE SET NULL
);
```

## Bảng đếm report (thay thế cho count trong bảng report)

```sql
CREATE TABLE "report_counter" (
    target_id UUID NOT NULL,
    target_type VARCHAR(20) NOT NULL,
    count INTEGER DEFAULT 1,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (target_id, target_type)
);
```
