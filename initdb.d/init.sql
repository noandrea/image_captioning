create table captions(
  hexdigest varchar(1000) primary key,
  file_name varchar(1000) not null,
  caption text not null,
  probability float,
  created_at timestamp default CURRENT_TIMESTAMP
)
