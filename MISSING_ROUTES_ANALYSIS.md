# Missing Admin Routes Analysis

## 📊 Summary

Based on analysis of:
- **Sidebar menus:** `resources/views/admin/includes/sidebar/`
- **Controllers:** `app/Http/Controllers/Admin/` (148 files found)
- **Existing routes:** `routes/admin.php`

---

## 🔴 Missing Routes from EDUCATION Section

| Menu Item | URL | Controller | Status |
|-----------|-----|------------|--------|
| Agora History | `/agora_history` | `AgoraHistoryController` | ❌ Missing |
| Course Notes | `/webinars/personal-notes` | `CoursePersonalNotesController` | ❌ Missing |
| Upcoming Courses - New | `/upcoming_courses/new` | `UpcomingCourseController` | ❌ Missing |
| Upcoming Courses - List | `/upcoming_courses` | `UpcomingCourseController` | ❌ Missing |
| Events - Create | `/events/create` | `EventsController` | ❌ Missing |
| Events - List | `/events` | `EventsController` | ❌ Missing |
| Events - Sold Tickets | `/events/sold-tickets` | `EventSoldTicketsController` | ❌ Missing |
| Events - Settings | `/events/settings` | `EventSettingsController` | ❌ Missing |
| Course Forum | `/webinars/course_forums` | `CourseForumController` | ❌ Missing |
| Course Notices - Send | `/course-noticeboards/send` | `CourseNoticeboardController` | ❌ Missing |
| Course Notices - List | `/course-noticeboards` | `CourseNoticeboardController` | ❌ Missing |
| Enrollments - Add | `/enrollments/add-student-to-class` | `EnrollmentController` | ❌ Missing |
| Enrollments - History | `/enrollments/history` | `EnrollmentController` | ❌ Missing |
| Waitlists | `/waitlists` | `WaitlistController` | ❌ Missing |
| Category Trends | `/categories/trends` | `CategoryController` | ❌ Missing |
| Attendances | `/attendances` | `AttendanceController` | ❌ Missing |
| Attendances Settings | `/attendances/settings` | `AttendanceController` | ❌ Missing |

---

## 🔴 Missing Routes from OTHER Sections (Partial)

Based on 148 controllers found, these are likely missing:

### Users Section
| Controller | Likely URL |
|------------|-----------|
| `DeleteAccountRequestsController` | `/delete-account-requests` |
| `ConsultantsController` | `/consultants/*` |

### Financial Section
| Controller | Likely URL |
|------------|-----------|
| `CashbackRuleController` | `/cashback/*` |
| `CashbackTransactionsController` | `/cashback/transactions` |
| `InstallmentController` | `/installments/*` |
| `RefundsController` | `/refunds/*` |
| `RegistrationPackagesController` | `/registration-packages/*` |

### Marketing Section
| Controller | Likely URL |
|------------|-----------|
| `AbandonedCartController` | `/abandoned-cart/*` |
| `AbandonedCartRulesController` | `/abandoned-cart/rules` |
| `AbandonedUsersCartController` | `/abandoned-users-cart` |
| `AdvertisingBannersController` | `/advertising/banners` |
| `AdvertisingModalController` | `/advertising/modal` |
| `CartDiscountController` | `/cart-discounts/*` |
| `FeatureWebinarController` | `/feature-webinars/*` |
| `GiftsController` | `/gifts/*` |
| `PromotionsController` | `/promotions/*` |
| `ReferralsController` | `/referrals/*` |
| `SeoController` | `/seo/*` |

### Content Section
| Controller | Likely URL |
|------------|-----------|
| `AIContentsController` | `/ai-contents/*` |
| `AIContentTemplatesController` | `/ai-contents/templates` |
| `FormsController` | `/forms/*` |
| `LandingsController` | `/landings/*` |
| `NewslettersController` | `/newsletters/*` |
| `SlidersController` | `/sliders/*` |

### Appearance Section
| Controller | Likely URL |
|------------|-----------|
| `ThemesController` | `/themes/*` |
| `HomeSectionsController` | `/home-sections/*` |
| `ThemeBuilderController` | `/theme-builder/*` |

### Settings Section
| Controller | Likely URL |
|------------|-----------|
| `GeneralSettingsController` | `/settings/general` |
| `FinancialSettingsController` | `/settings/financial` |
| `NotificationSettingsController` | `/settings/notifications` |
| `StorageSettingsController` | `/settings/storage` |
| `SocialMediaSettingsController` | `/settings/social-media` |
| many more...

---

## 📈 Statistics

| Category | Count |
|----------|-------|
| Total Admin Controllers | 148 |
| Existing Routes in admin.php | ~60 |
| **Estimated Missing Routes** | **~88** |

---

## ✅ How to Add Missing Routes

For each missing route, add to `routes/admin.php`:

```php
// Example for Events
Route::group(['prefix' => 'events'], function () {
    Route::get('/', 'EventsController@index');
    Route::get('/create', 'EventsController@create');
    Route::post('/', 'EventsController@store');
    Route::get('/{id}/edit', 'EventsController@edit');
    Route::put('/{id}', 'EventsController@update');
    Route::delete('/{id}', 'EventsController@destroy');
    Route::get('/settings', 'EventSettingsController@index');
    Route::post('/settings', 'EventSettingsController@store');
    Route::get('/sold-tickets', 'EventSoldTicketsController@index');
});
```

---

*Generated: 2024-12-27*
