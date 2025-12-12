- [ ] Improve Error Handling
- [ ] Add Logger
- [ ] Add Tests
- [ ] Add Spotify integration
- [ ] Add Schemas
- [ ] Rewrite Docker file
- [ ] Rewrite README.md

Commands:

```
uvicorn app.main:app --reload
celery -A worker.celery_app worker --loglevel=info

```
