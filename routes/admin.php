<?php

use Illuminate\Support\Facades\Route;

/*
|--------------------------------------------------------------------------
| Admin Routes
|--------------------------------------------------------------------------
*/

// Admin Auth Routes - NO ADMIN MIDDLEWARE (to prevent redirect loop)
Route::group(['prefix' => 'admin', 'namespace' => 'Admin', 'middleware' => ['web']], function () {
    Route::get('/login', 'LoginController@showLoginForm')->name('admin.login');
    Route::post('/login', 'LoginController@login')->name('admin.login.post');
    Route::get('/logout', 'LoginController@logout')->name('admin.logout');
    Route::post('/logout', 'LoginController@logout')->name('admin.logout.post');
});

// Protected Admin Routes - REQUIRES ADMIN MIDDLEWARE
Route::group(['prefix' => 'admin', 'namespace' => 'Admin', 'middleware' => ['web', 'admin']], function () {

    // Dashboard
    Route::get('/', 'DashboardController@index')->name('admin.dashboard');
    Route::get('/dashboard', 'DashboardController@index')->name('admin.dashboard.index');
    Route::get('/dashboard/statistics', 'DashboardController@index');

    // Settings - CRITICAL
    Route::group(['prefix' => 'settings'], function () {
        Route::get('/', 'SettingsController@index')->name('admin.settings');
        Route::get('/update-app', 'UpdateController@index')->name('admin.settings.update_app');
        Route::get('/{page}', 'SettingsController@page')->name('admin.settings.page');
        Route::post('/{name}/store', 'SettingsController@store')->name('admin.settings.store');
        Route::post('/{name}', 'SettingsController@store'); // Added to fix 404 on financial, features, etc.
        Route::get('/seo/{page}', 'SettingsController@page');
        Route::post('/seo/metas', 'SettingsController@storeSeoMetas');
        Route::get('/socials/{key}/edit', 'SettingsController@editSocials');
        Route::post('/socials/store', 'SettingsController@storeSocials');
        Route::get('/socials/{key}/delete', 'SettingsController@deleteSocials');
        Route::get('/personalization/{name}', 'SettingsController@personalizationPage');
        Route::post('/notifications/metas', 'SettingsController@notificationsMetas');
    });

    // Appearance & Customization
    Route::group(['prefix' => 'appearance'], function () {
        // Themes
        Route::group(['prefix' => 'themes'], function () {
            Route::get('/', 'ThemesController@index')->name('admin.appearance.themes.index');
            Route::get('/create', 'ThemesController@create')->name('admin.appearance.themes.create');
            Route::post('/store', 'ThemesController@store')->name('admin.appearance.themes.store');
            Route::get('/{id}/edit', 'ThemesController@edit')->name('admin.appearance.themes.edit');
            Route::post('/{id}/update', 'ThemesController@update')->name('admin.appearance.themes.update');
            Route::get('/{id}/delete', 'ThemesController@delete')->name('admin.appearance.themes.delete');
            Route::get('/{id}/enable', 'ThemesController@enable')->name('admin.appearance.themes.enable');
        });

        // Home Sections
        Route::group(['prefix' => 'home-sections'], function () {
            Route::get('/', 'HomeSectionSettingsController@index')->name('admin.appearance.home_sections.index');
            Route::post('/store', 'HomeSectionSettingsController@store')->name('admin.appearance.home_sections.store');
            Route::get('/{id}/delete', 'HomeSectionSettingsController@delete')->name('admin.appearance.home_sections.delete');
            Route::post('/sort', 'HomeSectionSettingsController@sort')->name('admin.appearance.home_sections.sort');
        });

        // Theme Builder (Sub-components)
        Route::group(['prefix' => 'theme-builder'], function () {
            Route::resource('colors', 'ThemeColorsController')->names('admin.appearance.theme_builder.colors');
            Route::resource('fonts', 'ThemeFontsController')->names('admin.appearance.theme_builder.fonts');
            Route::resource('headers', 'ThemeHeadersController')->names('admin.appearance.theme_builder.headers');
            Route::resource('footers', 'ThemeFootersController')->names('admin.appearance.theme_builder.footers');
        });

        // Additional Pages
        Route::resource('additional_pages', 'AdditionalPageController')->names('admin.appearance.additional_pages');
    });

    // Landing Builder (Controller is in App\Http\Controllers\LandingBuilder)
    Route::group(['prefix' => 'landing-builder'], function () {
        Route::get('/', [\App\Http\Controllers\LandingBuilder\LandingBuilderController::class, 'welcome'])->name('admin.landing_builder');
        Route::get('/landings', [\App\Http\Controllers\LandingBuilder\LandingBuilderController::class, 'index'])->name('admin.landing_builder.index');
        Route::get('/create', [\App\Http\Controllers\LandingBuilder\LandingBuilderController::class, 'create'])->name('admin.landing_builder.create');
        Route::post('/store', [\App\Http\Controllers\LandingBuilder\LandingBuilderController::class, 'store'])->name('admin.landing_builder.store');
        Route::get('/{id}/edit', [\App\Http\Controllers\LandingBuilder\LandingBuilderController::class, 'edit'])->name('admin.landing_builder.edit');
        Route::post('/{id}/update', [\App\Http\Controllers\LandingBuilder\LandingBuilderController::class, 'update'])->name('admin.landing_builder.update');
        Route::get('/{id}/delete', [\App\Http\Controllers\LandingBuilder\LandingBuilderController::class, 'delete'])->name('admin.landing_builder.delete');
        Route::get('/{id}/duplicate', [\App\Http\Controllers\LandingBuilder\LandingBuilderController::class, 'duplicate'])->name('admin.landing_builder.duplicate');
        Route::post('/{id}/sort-components', [\App\Http\Controllers\LandingBuilder\LandingBuilderController::class, 'sortComponents'])->name('admin.landing_builder.sort_components');
        Route::get('/component-preview/{name}', [\App\Http\Controllers\LandingBuilder\LandingBuilderController::class, 'componentPreview'])->name('admin.landing_builder.component_preview');
        Route::get('/all-landing-pages', [\App\Http\Controllers\LandingBuilder\LandingBuilderController::class, 'allLandingPages'])->name('admin.landing_builder.all_landing_pages');
        Route::get('/start', [\App\Http\Controllers\LandingBuilder\LandingBuilderController::class, 'welcome'])->name('admin.landing_builder.start');
        Route::get('/all-pages', [\App\Http\Controllers\LandingBuilder\LandingBuilderController::class, 'allLandingPages'])->name('admin.landing_builder.all_pages');

        // Landing Components
        Route::group(['prefix' => '{landingId}/components'], function () {
            Route::post('/add', [\App\Http\Controllers\LandingBuilder\LandingBuilderComponentController::class, 'add'])->name('admin.landing_builder.components.add');
            Route::get('/{componentId}/edit', [\App\Http\Controllers\LandingBuilder\LandingBuilderComponentController::class, 'edit'])->name('admin.landing_builder.components.edit');
            Route::post('/{componentId}/update', [\App\Http\Controllers\LandingBuilder\LandingBuilderComponentController::class, 'update'])->name('admin.landing_builder.components.update');
            Route::get('/{componentId}/duplicate', [\App\Http\Controllers\LandingBuilder\LandingBuilderComponentController::class, 'duplicate'])->name('admin.landing_builder.components.duplicate');
            Route::get('/{componentId}/clear-content', [\App\Http\Controllers\LandingBuilder\LandingBuilderComponentController::class, 'clearContent'])->name('admin.landing_builder.components.clear_content');
            Route::get('/{componentId}/disable', [\App\Http\Controllers\LandingBuilder\LandingBuilderComponentController::class, 'disable'])->name('admin.landing_builder.components.disable');
            Route::get('/{componentId}/enable', [\App\Http\Controllers\LandingBuilder\LandingBuilderComponentController::class, 'enable'])->name('admin.landing_builder.components.enable');
            Route::get('/{componentId}/delete', [\App\Http\Controllers\LandingBuilder\LandingBuilderComponentController::class, 'delete'])->name('admin.landing_builder.components.delete');
        });
    });

    // Pages (Static)
    Route::resource('pages', 'PagesController')->names('admin.pages');

    // Alternative routes for Themes (direct URL access)
    Route::get('/themes', 'ThemesController@index')->name('admin.themes.index');
    Route::get('/themes/create', 'ThemesController@create')->name('admin.themes.create');
    Route::post('/themes/store', 'ThemesController@store')->name('admin.themes.store');
    Route::get('/themes/{id}/edit', 'ThemesController@edit')->name('admin.themes.edit');
    Route::post('/themes/{id}/update', 'ThemesController@update')->name('admin.themes.update');
    Route::get('/themes/{id}/delete', 'ThemesController@delete')->name('admin.themes.delete');
    Route::get('/themes/{id}/enable', 'ThemesController@enable')->name('admin.themes.enable');
    Route::get('/themes/get-home-landing-components', 'ThemesController@getHomeLandingComponents');

    // Alternative routes for Landings (direct URL access)
    Route::get('/landings', 'LandingBuilder\\LandingBuilderController@index')->name('admin.landings.index');
    Route::get('/landings/create', 'LandingBuilder\\LandingBuilderController@create')->name('admin.landings.create');
    Route::post('/landings/store', 'LandingBuilder\\LandingBuilderController@store')->name('admin.landings.store');
    Route::get('/landings/{id}/edit', 'LandingBuilder\\LandingBuilderController@edit')->name('admin.landings.edit');
    Route::post('/landings/{id}/update', 'LandingBuilder\\LandingBuilderController@update')->name('admin.landings.update');
    Route::get('/landings/{id}/delete', 'LandingBuilder\\LandingBuilderController@delete')->name('admin.landings.delete');
    Route::get('/landings/{id}/duplicate', 'LandingBuilder\\LandingBuilderController@duplicate')->name('admin.landings.duplicate');
    Route::post('/landings/{id}/sort-components', 'LandingBuilder\\LandingBuilderController@sortComponents');
    Route::get('/landings/all', 'LandingBuilder\\LandingBuilderController@allLandingPages');


    // Users
    Route::group(['prefix' => 'users'], function () {
        Route::get('/', 'UserController@index')->name('admin.users.index');
        Route::get('/create', 'UserController@create')->name('admin.users.create');
        Route::post('/', 'UserController@store')->name('admin.users.store');
        Route::get('/{id}', 'UserController@show')->name('admin.users.show');
        Route::get('/{id}/edit', 'UserController@edit')->name('admin.users.edit');
        Route::post('/{id}/update', 'UserController@update')->name('admin.users.update');
        Route::get('/{id}/delete', 'UserController@destroy')->name('admin.users.destroy');
        Route::get('/{id}/impersonate', 'UserController@impersonate');
        Route::get('/{id}/financial', 'UserController@financial');
        Route::post('/{id}/financial', 'UserController@updateFinancial');
    });

    // Staffs/Admins
    Route::group(['prefix' => 'staffs'], function () {
        Route::get('/', 'UserController@staffs')->name('admin.staffs.index');
        Route::get('/create', 'UserController@create');
        Route::post('/', 'UserController@store');
    });

    // Students
    Route::group(['prefix' => 'students'], function () {
        Route::get('/', 'UserController@students')->name('admin.students.index');
    });

    // Instructors
    Route::group(['prefix' => 'instructors'], function () {
        Route::get('/', 'UserController@instructors')->name('admin.instructors.index');
    });

    // Organizations
    Route::group(['prefix' => 'organizations'], function () {
        Route::get('/', 'UserController@organizations')->name('admin.organizations.index');
    });

    // Webinars/Courses
    Route::group(['prefix' => 'webinars'], function () {
        Route::get('/', 'WebinarController@index')->name('admin.webinars.index');
        Route::get('/create', 'WebinarController@create')->name('admin.webinars.create');
        Route::post('/', 'WebinarController@store')->name('admin.webinars.store');
        Route::get('/{id}', 'WebinarController@show')->name('admin.webinars.show');
        Route::get('/{id}/edit', 'WebinarController@edit')->name('admin.webinars.edit');
        Route::post('/{id}/update', 'WebinarController@update')->name('admin.webinars.update');
        Route::get('/{id}/delete', 'WebinarController@destroy')->name('admin.webinars.destroy');
        Route::get('/{id}/students', 'WebinarController@studentsLists');
        Route::get('/{id}/export-students-list', 'WebinarController@exportExcel');
        Route::get('/{id}/statistics', 'WebinarStatisticController@index');
        Route::get('/{id}/sendNotification', 'WebinarController@notificationToStudents');
        Route::post('/{id}/sendNotification', 'WebinarController@sendNotificationToStudents');
        Route::get('/{id}/approve', 'WebinarController@approve');
        Route::get('/{id}/reject', 'WebinarController@reject');
        Route::get('/{id}/unpublish', 'WebinarController@unpublish');
    });

    // Course Personal Notes
    Route::group(['prefix' => 'webinars/personal-notes'], function () {
        Route::get('/', 'CoursePersonalNotesController@index');
        Route::get('/{id}/download-attachment', 'CoursePersonalNotesController@downloadAttachment');
        Route::post('/{id}/update', 'CoursePersonalNotesController@update');
        Route::get('/{id}/delete', 'CoursePersonalNotesController@delete');
    });

    // Course Noticeboards
    Route::group(['prefix' => 'course-noticeboards'], function () {
        Route::get('/', 'CourseNoticeboardController@index');
        Route::get('/create', 'CourseNoticeboardController@create');
        Route::post('/store', 'CourseNoticeboardController@store');
        Route::get('/{id}/edit', 'CourseNoticeboardController@edit');
        Route::post('/{id}/update', 'CourseNoticeboardController@update');
        Route::get('/{id}/delete', 'CourseNoticeboardController@delete');
    });

    // Course Forums
    Route::group(['prefix' => 'webinars/course_forums'], function () {
        Route::get('/', 'CourseForumsControllers@index');
        Route::get('/{webinar_id}/forums', 'CourseForumsControllers@forums');
        Route::get('/{webinar_id}/forums/{forum_id}/answers', 'CourseForumsControllers@answers');
        Route::get('/{webinar_id}/forums/{forum_id}/edit', 'CourseForumsControllers@forumEdit');
        Route::post('/{webinar_id}/forums/{forum_id}/update', 'CourseForumsControllers@forumUpdate');
        Route::get('/{webinar_id}/forums/{forum_id}/delete', 'CourseForumsControllers@forumDelete');
        Route::get('/{webinar_id}/forums/{forum_id}/answers/{id}/edit', 'CourseForumsControllers@answerEdit');
        Route::get('/{webinar_id}/forums/{forum_id}/answers/{id}/delete', 'CourseForumsControllers@answerDelete');
        Route::post('/{webinar_id}/forums/{forum_id}/answers/{id}/update', 'CourseForumsControllers@answerUpdate');
    });

    // Agora History
    Route::group(['prefix' => 'agora_history'], function () {
        Route::get('/', 'AgoraHistoryController@index');
        Route::get('/export', 'AgoraHistoryController@exportExcel');
    });

    // Upcoming Courses
    Route::group(['prefix' => 'upcoming_courses'], function () {
        Route::get('/', 'UpcomingCoursesController@index');
        Route::get('/new', 'UpcomingCoursesController@create');
        Route::post('/store', 'UpcomingCoursesController@store');
        Route::get('/{id}/edit', 'UpcomingCoursesController@edit');
        Route::post('/{id}/update', 'UpcomingCoursesController@update');
        Route::get('/{id}/delete', 'UpcomingCoursesController@destroy');
        Route::get('/{id}/approve', 'UpcomingCoursesController@approve');
        Route::get('/{id}/reject', 'UpcomingCoursesController@reject');
        Route::get('/{id}/unpublish', 'UpcomingCoursesController@unpublish');
        Route::get('/export', 'UpcomingCoursesController@exportExcel');
        Route::get('/{id}/followers', 'UpcomingCoursesController@followers');
    });

    // Attendances
    Route::group(['prefix' => 'attendances'], function () {
        Route::get('/', 'AttendanceController@index');
        Route::get('/export', 'AttendanceController@exportExcel');
        Route::get('/settings', 'AttendanceController@settings');
        Route::post('/settings', 'AttendanceController@storeSettings');
    });

    // Waitlists
    Route::group(['prefix' => 'waitlists'], function () {
        Route::get('/', 'WaitlistController@index');
        Route::get('/export', 'WaitlistController@exportExcel');
        Route::get('/{id}/view_list', 'WaitlistController@viewList');
        Route::get('/{id}/export_list', 'WaitlistController@exportUsersList');
        Route::get('/{id}/clear_list', 'WaitlistController@clearList');
        Route::get('/{id}/disable', 'WaitlistController@disableWaitlist');
        Route::get('/items/{id}/delete', 'WaitlistController@deleteWaitlistItems');
    });

    // Events
    Route::group(['prefix' => 'events'], function () {
        Route::get('/', 'EventsController@index');
        Route::get('/create', 'EventsController@create');
        Route::post('/store', 'EventsController@store');
        Route::get('/{id}/edit', 'EventsController@edit');
        Route::post('/{id}/update', 'EventsController@update');
        Route::get('/{id}/delete', 'EventsController@delete');
        Route::get('/{id}/export', 'EventsController@exportExcel');
        Route::get('/{id}/sendNotification', 'EventsController@notificationToStudents');
        Route::post('/{id}/sendNotification', 'EventsController@sendNotificationToStudents');
    });

    // Categories
    Route::group(['prefix' => 'categories'], function () {
        Route::get('/', 'CategoryController@index')->name('admin.categories.index');
        Route::get('/create', 'CategoryController@create')->name('admin.categories.create');
        Route::post('/', 'CategoryController@store')->name('admin.categories.store');
        Route::get('/{id}/edit', 'CategoryController@edit')->name('admin.categories.edit');
        Route::post('/{id}/update', 'CategoryController@update')->name('admin.categories.update');
        Route::get('/{id}/delete', 'CategoryController@destroy')->name('admin.categories.destroy');
    });

    // Filters
    Route::group(['prefix' => 'filters'], function () {
        Route::get('/', 'FilterController@index')->name('admin.filters.index');
        Route::get('/create', 'FilterController@create');
        Route::post('/', 'FilterController@store');
        Route::get('/{id}/edit', 'FilterController@edit');
        Route::post('/{id}/update', 'FilterController@update');
        Route::get('/{id}/delete', 'FilterController@destroy');
    });

    // Quizzes
    Route::group(['prefix' => 'quizzes'], function () {
        Route::get('/', 'QuizController@index')->name('admin.quizzes.index');
        Route::get('/create', 'QuizController@create');
        Route::post('/', 'QuizController@store');
        Route::get('/{id}/edit', 'QuizController@edit');
        Route::post('/{id}/update', 'QuizController@update');
        Route::get('/{id}/delete', 'QuizController@delete');
        Route::get('/results', 'QuizController@results');
    });



    // Financial 
    Route::group(['prefix' => 'financial'], function () {
        Route::get('/sales', 'SaleController@index')->name('admin.financial.sales');
        Route::get('/sales/export', 'SaleController@export');
        Route::get('/payouts', 'PayoutController@index')->name('admin.financial.payouts');
        Route::get('/payouts/{id}/confirm', 'PayoutController@confirm');
        Route::get('/payouts/{id}/reject', 'PayoutController@reject');
        Route::get('/offline-payments', 'OfflinePaymentController@index');
        Route::get('/offline-payments/{id}/approve', 'OfflinePaymentController@approve');
        Route::get('/offline-payments/{id}/reject', 'OfflinePaymentController@reject');
        Route::get('/documents', 'DocumentController@index');
        Route::get('/subscribes', 'SubscribeController@index');
        Route::get('/registration-packages', 'RegistrationPackagesController@index');
        Route::get('/discounts', 'DiscountController@index');
        Route::get('/discount/create', 'DiscountController@create');
        Route::post('/discount', 'DiscountController@store');
    });

    // Marketing
    Route::group(['prefix' => 'marketing'], function () {
        Route::get('/', 'PromotionsController@index')->name('admin.marketing.index');
        Route::get('/promotions', 'PromotionsController@index')->name('admin.marketing.promotions');
        Route::get('/promotions/create', 'PromotionsController@create');
        Route::post('/promotions', 'PromotionsController@store');
        Route::get('/promotions/{id}/edit', 'PromotionsController@edit');
        Route::post('/promotions/{id}/update', 'PromotionsController@update');
        Route::get('/promotions/{id}/delete', 'PromotionsController@delete');
        Route::get('/advertising', 'AdvertisingBannersController@index')->name('admin.marketing.advertising');
        Route::get('/newsletters', 'NewslettersController@index')->name('admin.marketing.newsletters');
        Route::get('/notifications', 'NotificationsController@index')->name('admin.marketing.notifications');
        Route::get('/featured', 'FeaturedTopicsController@index')->name('admin.marketing.featured');
    });

    // Blog
    Route::group(['prefix' => 'blog'], function () {
        Route::get('/', 'BlogController@index')->name('admin.blog.index');
        Route::get('/create', 'BlogController@create');
        Route::post('/', 'BlogController@store');
        Route::get('/{id}/edit', 'BlogController@edit');
        Route::post('/{id}/update', 'BlogController@update');
        Route::get('/{id}/delete', 'BlogController@destroy');
        Route::get('/categories', 'BlogCategoriesController@index');
    });

    // Pages
    Route::group(['prefix' => 'pages'], function () {
        Route::get('/', 'AdditionalPageController@index')->name('admin.pages.index');
        Route::get('/create', 'AdditionalPageController@create');
        Route::post('/', 'AdditionalPageController@store');
        Route::get('/{id}/edit', 'AdditionalPageController@edit');
        Route::post('/{id}/update', 'AdditionalPageController@update');
        Route::get('/{id}/delete', 'AdditionalPageController@destroy');
    });

    // Testimonials
    Route::group(['prefix' => 'testimonials'], function () {
        Route::get('/', 'TestimonialsController@index');
        Route::get('/create', 'TestimonialsController@create');
        Route::post('/', 'TestimonialsController@store');
        Route::get('/{id}/edit', 'TestimonialsController@edit');
        Route::post('/{id}/update', 'TestimonialsController@update');
        Route::get('/{id}/delete', 'TestimonialsController@destroy');
    });

    // FAQ
    Route::group(['prefix' => 'faqs'], function () {
        Route::get('/', 'FAQController@index');
        Route::get('/create', 'FAQController@create');
        Route::post('/', 'FAQController@store');
        Route::get('/{id}/edit', 'FAQController@edit');
        Route::post('/{id}/update', 'FAQController@update');
        Route::get('/{id}/delete', 'FAQController@destroy');
    });

    // Supports/Tickets
    Route::group(['prefix' => 'supports'], function () {
        Route::get('/', 'SupportsController@index');
        Route::get('/{id}', 'SupportsController@show');
        Route::post('/{id}/reply', 'SupportsController@reply');
        Route::get('/{id}/close', 'SupportsController@close');
        Route::get('/departments', 'SupportDepartmentController@index');
    });

    // Comments
    Route::group(['prefix' => 'comments'], function () {
        Route::get('/', 'CommentsController@index');
        Route::get('/webinars', 'CommentsController@webinars');
        Route::get('/bundles', 'CommentsController@bundles');
        Route::get('/blog', 'CommentsController@blog');
        Route::get('/products', 'CommentsController@products');
        Route::get('/{id}/toggle-status', 'CommentsController@toggleStatus');
        Route::get('/{id}/edit', 'CommentsController@edit');
        Route::get('/{id}/reply', 'CommentsController@reply');
        Route::get('/{id}/delete', 'CommentsController@destroy');
    });

    // Reports
    Route::group(['prefix' => 'reports'], function () {
        Route::get('/', 'ReportsController@index');
        Route::get('/reasons', 'ReportReasonsController@index');
        Route::get('/webinars', 'ReportsController@webinars');
        Route::get('/comments', 'ReportsController@comments');
    });

    // Contacts
    Route::group(['prefix' => 'contacts'], function () {
        Route::get('/', 'ContactController@index');
        Route::get('/{id}', 'ContactController@show');
        Route::get('/{id}/delete', 'ContactController@destroy');
    });

    // Notifications
    Route::group(['prefix' => 'notifications'], function () {
        Route::get('/', 'NotificationsController@index');
        Route::get('/create', 'NotificationsController@create');
        Route::post('/', 'NotificationsController@store');
        Route::get('/{id}/edit', 'NotificationsController@edit');
        Route::post('/{id}/update', 'NotificationsController@update');
        Route::get('/{id}/delete', 'NotificationsController@destroy');
    });

    // Noticeboard
    Route::group(['prefix' => 'noticeboard'], function () {
        Route::get('/', 'NoticeboardController@index');
        Route::get('/create', 'NoticeboardController@create');
        Route::post('/', 'NoticeboardController@store');
        Route::get('/{id}/edit', 'NoticeboardController@edit');
        Route::post('/{id}/update', 'NoticeboardController@update');
        Route::get('/{id}/delete', 'NoticeboardController@destroy');
    });

    // Roles
    Route::group(['prefix' => 'roles'], function () {
        Route::get('/', 'RolesController@index');
        Route::get('/create', 'RolesController@create');
        Route::post('/', 'RolesController@store');
        Route::get('/{id}/edit', 'RolesController@edit');
        Route::post('/{id}/update', 'RolesController@update');
        Route::get('/{id}/delete', 'RolesController@destroy');
    });

    // Groups
    Route::group(['prefix' => 'groups'], function () {
        Route::get('/', 'GroupsController@index');
        Route::get('/create', 'GroupsController@create');
        Route::post('/', 'GroupsController@store');
        Route::get('/{id}/edit', 'GroupsController@edit');
        Route::post('/{id}/update', 'GroupsController@update');
        Route::get('/{id}/delete', 'GroupsController@destroy');
    });

    // Badges
    Route::group(['prefix' => 'badges'], function () {
        Route::get('/', 'BadgesController@index');
        Route::get('/create', 'BadgesController@create');
        Route::post('/', 'BadgesController@store');
        Route::get('/{id}/edit', 'BadgesController@edit');
        Route::post('/{id}/update', 'BadgesController@update');
        Route::get('/{id}/delete', 'BadgesController@destroy');
    });

    // Regions
    Route::group(['prefix' => 'regions'], function () {
        Route::get('/countries', 'RegionController@countries');
        Route::get('/provinces', 'RegionController@provinces');
        Route::get('/cities', 'RegionController@cities');
        Route::get('/districts', 'RegionController@districts');
    });

    // Products (Store)
    Route::group(['prefix' => 'store'], function () {
        Route::get('/products', 'ProductController@index');
        Route::get('/products/create', 'ProductController@create');
        Route::post('/products', 'ProductController@store');
        Route::get('/products/{id}/edit', 'ProductController@edit');
        Route::post('/products/{id}/update', 'ProductController@update');
        Route::get('/products/{id}/delete', 'ProductController@destroy');
        Route::get('/categories', 'ProductCategoryController@index');
        Route::get('/orders', 'ProductOrderController@index');
        Route::get('/reviews', 'ProductReviewController@index');
    });

    // Bundles
    Route::group(['prefix' => 'bundles'], function () {
        Route::get('/', 'BundleController@index');
        Route::get('/create', 'BundleController@create');
        Route::post('/', 'BundleController@store');
        Route::get('/{id}/edit', 'BundleController@edit');
        Route::post('/{id}/update', 'BundleController@update');
        Route::get('/{id}/delete', 'BundleController@destroy');
    });

    // Forums
    Route::group(['prefix' => 'forums'], function () {
        Route::get('/', 'ForumsController@index');
        Route::get('/topics', 'ForumsTopicController@index');
        Route::get('/posts', 'ForumsTopicPostController@index');
    });

    // Assignments
    Route::group(['prefix' => 'assignments'], function () {
        Route::get('/', 'AssignmentController@index')->name('admin.assignments.index');
        Route::get('/history', 'AssignmentController@index')->name('admin.assignments.history'); // Fallback to index if history controller missing
        Route::get('/{id}/students', 'AssignmentController@students')->name('admin.assignments.students');
        Route::get('/{id}/conversations/{history_id}', 'AssignmentController@conversations')->name('admin.assignments.conversations');
        Route::get('/{id}/delete', 'AssignmentController@destroy')->name('admin.assignments.delete');
    });

    // Enrollments
    Route::group(['prefix' => 'enrollments'], function () {
        Route::get('/manual', 'EnrollmentController@manual');
        Route::post('/manual', 'EnrollmentController@storeManual');
        Route::get('/history', 'EnrollmentController@history');
    });

    // AI Content
    Route::group(['prefix' => 'ai-contents'], function () {
        Route::get('/', 'AIContentsController@index');
        Route::get('/templates', 'AIContentTemplatesController@index');
    });

    // Reviews/Ratings
    Route::group(['prefix' => 'reviews'], function () {
        Route::get('/', 'ReviewsController@index');
        Route::get('/webinars', 'ReviewsController@webinars');
        Route::get('/bundles', 'ReviewsController@bundles');
        Route::get('/{id}/toggle-status', 'ReviewsController@toggleStatus');
        Route::get('/{id}/delete', 'ReviewsController@delete');
    });

    // Consultants/Meetings
    Route::group(['prefix' => 'consultants'], function () {
        Route::get('/', 'ConsultantsController@index');
        Route::get('/appointments', 'AppointmentsController@index');
    });

    // Reward Points
    Route::group(['prefix' => 'rewards'], function () {
        Route::get('/', 'RewardPointsController@index');
        Route::get('/settings', 'RewardPointsController@settings');
    });

    // Become Instructor
    Route::group(['prefix' => 'become-instructors'], function () {
        Route::get('/', 'BecomeInstructorController@index');
        Route::get('/{id}/reject', 'BecomeInstructorController@reject');
        Route::get('/{id}/accept', 'BecomeInstructorController@accept');
    });



    /*
    // Licenses (BYPASS - always returns valid)
    Route::group(['prefix' => 'licenses'], function () {
        Route::get('/', 'LicensesController@index')->name('admin.licenses.index');
        Route::post('/verify', 'LicensesController@verify');
        Route::post('/store', 'LicensesController@store')->name('admin.licenses.store');
    });

    // Plugin License
    Route::get('/plugin-license', 'LicensesController@index')->name('admin.plugin.license');
    Route::post('/plugin-license/store', 'LicensesController@store')->name('admin.plugin.license.store');

    // Mobile App License  
    Route::get('/mobile-license', 'LicensesController@index')->name('admin.mobile_app.license');
    Route::post('/mobile-license/store', 'LicensesController@store')->name('admin.mobile_app.license.store');

    // Theme Builder License
    Route::get('/theme-license', 'LicensesController@index')->name('admin.theme-builder.license');
    Route::post('/theme-license/store', 'LicensesController@store')->name('admin.theme-builder.license.store');
    */

    // Update Application
    Route::group(['prefix' => 'update'], function () {
        Route::get('/', 'UpdateController@index');
        Route::post('/basic-update', 'UpdateController@basicUpdate');
        Route::post('/custom-update', 'UpdateController@customUpdate');
        Route::post('/database-update', 'UpdateController@databaseUpdate');
    });

    // Mobile App Settings
    Route::group(['prefix' => 'settings/mobile-app'], function () {
        Route::get('/', 'MobileAppSettingsController@index');
        Route::get('/{name}', 'MobileAppSettingsController@index');
        Route::post('/store', 'MobileAppSettingsController@store');
    });

    // Mobile App License
    Route::group(['prefix' => 'mobile-app-license'], function () {
        Route::get('/', 'MobileAppLicenseController@index');
        Route::post('/store', 'MobileAppLicenseController@store');
    });

    // Translator
    Route::group(['prefix' => 'translator'], function () {
        Route::get('/', 'TranslatorController@index')->name('admin.translator.index');
        Route::post('/translate', 'TranslatorController@translate')->name('admin.translator.translate');
    });



    /*
    |--------------------------------------------------------------------------
    | Users Section Routes (Added for full functionality)
    |--------------------------------------------------------------------------
    */

    // User Lists - different views
    Route::get('/all-users', 'UserController@allUsers');
    Route::get('/all-users/excel', 'UserController@exportExcelAllUsers');
    Route::get('/staffs', 'UserController@staffs');
    Route::get('/students', 'UserController@students');
    Route::get('/students/excel', 'UserController@exportExcelStudents');
    Route::get('/instructors', 'UserController@instructors');
    Route::get('/instructors/excel', 'UserController@exportExcelInstructors');
    Route::get('/organizations', 'UserController@organizations');
    Route::get('/organizations/excel', 'UserController@exportExcelOrganizations');


    // Users CRUD & Actions
    Route::group(['prefix' => 'users'], function () {
        Route::get('/create', 'UserController@create');
        Route::post('/store', 'UserController@store');
        Route::get('/{id}/edit', 'UserController@edit');
        Route::post('/{id}/update', 'UserController@update');
        Route::get('/{id}/delete', 'UserController@destroy');
        Route::post('/{id}/update-image', 'UserController@updateImage');
        Route::post('/{id}/financial', 'UserController@financialUpdate');
        Route::post('/{id}/occupations', 'UserController@occupationsUpdate');
        Route::post('/{id}/badges', 'UserController@badgesUpdate');
        Route::get('/{id}/badge/{badge_id}/delete', 'UserController@deleteBadge');
        Route::get('/{id}/impersonate', 'UserController@impersonate');
        Route::get('/search', 'UserController@search');
        Route::get('/excel/all', 'UserController@exportExcelAllUsers');
        Route::get('/excel/students', 'UserController@exportExcelStudents');
        Route::get('/excel/instructors', 'UserController@exportExcelInstructors');
        Route::get('/excel/organizations', 'UserController@exportExcelOrganizations');

        // Not Access to Content
        Route::get('/not-access-to-content', 'UsersNotAccessToContentController@index');
        Route::get('/not-access-to-content/{id}/delete', 'UsersNotAccessToContentController@destroy');

        // User Badges (general)
        Route::get('/badges', 'BadgesController@index');
        Route::get('/badges/create', 'BadgesController@create');
        Route::post('/badges/store', 'BadgesController@store');
        Route::get('/badges/{id}/edit', 'BadgesController@edit');
        Route::post('/badges/{id}/update', 'BadgesController@update');
        Route::get('/badges/{id}/delete', 'BadgesController@destroy');

        // Delete Account Requests
        Route::get('/delete-account-requests', 'DeleteAccountRequestsController@index');
        Route::get('/delete-account-requests/{id}/confirm', 'DeleteAccountRequestsController@confirm');
        Route::get('/delete-account-requests/{id}/delete', 'DeleteAccountRequestsController@delete');

        // Login History
        Route::get('/login-history', 'UserLoginHistoryController@index');
        Route::get('/login-history/export', 'UserLoginHistoryController@export');
        Route::get('/login-history/{id}/end-session', 'UserLoginHistoryController@endSession');
        Route::get('/login-history/{id}/delete', 'UserLoginHistoryController@delete');
        Route::get('/login-history/user/{userId}/end-all', 'UserLoginHistoryController@endAllUserSessions');

        // IP Restriction
        Route::get('/ip-restriction', 'UserIpRestrictionController@index');
        Route::get('/ip-restriction/form', 'UserIpRestrictionController@getForm');
        Route::post('/ip-restriction/store', 'UserIpRestrictionController@store');
        Route::get('/ip-restriction/{id}/edit', 'UserIpRestrictionController@edit');
        Route::post('/ip-restriction/{id}/update', 'UserIpRestrictionController@update');
        Route::get('/ip-restriction/{id}/delete', 'UserIpRestrictionController@delete');

        // User Groups (already may exist but ensuring complete)
        Route::group(['prefix' => 'groups'], function () {
            Route::get('/', 'GroupController@index');
            Route::get('/create', 'GroupController@create');
            Route::post('/store', 'GroupController@store');
            Route::get('/{id}/edit', 'GroupController@edit');
            Route::post('/{id}/update', 'GroupController@update');
            Route::get('/{id}/delete', 'GroupController@destroy');
        });
    });

    /*
    |--------------------------------------------------------------------------
    | Education Section Routes (Added for full functionality)
    |--------------------------------------------------------------------------
    */

    // Certificates (Quiz-based)
    Route::group(['prefix' => 'certificates'], function () {
        Route::get('/', 'CertificateController@index');
        Route::get('/excel', 'CertificateController@exportExcel');
        Route::get('/{id}/download', 'CertificateController@CertificatesDownload');

        // Course/Competition Certificates
        Route::get('/course-competition', 'WebinarCertificateController@index');
        Route::get('/course-competition/{id}', 'WebinarCertificateController@show');

        // Certificate Templates
        Route::get('/templates', 'CertificateController@CertificatesTemplatesList');
        Route::get('/templates/new', 'CertificateController@CertificatesNewTemplate');
        Route::post('/templates/store', 'CertificateController@CertificatesTemplateStore');
        Route::get('/templates/{template_id}/edit', 'CertificateController@CertificatesTemplatesEdit');
        Route::post('/templates/{template_id}/update', 'CertificateController@CertificatesTemplateStore');
        Route::get('/templates/{template_id}/delete', 'CertificateController@CertificatesTemplatesDelete');
        Route::post('/templates/preview', 'CertificateController@CertificatesTemplatePreview');

        // Certificate Settings
        Route::get('/settings', 'CertificateController@settings');
        Route::post('/settings/store', 'CertificateController@storeSettings');
    });

    // Upcoming Courses
    Route::group(['prefix' => 'upcoming_courses'], function () {
        Route::get('/', 'UpcomingCoursesController@index');
        Route::get('/new', 'UpcomingCoursesController@create');
        Route::post('/store', 'UpcomingCoursesController@store');
        Route::get('/{id}/edit', 'UpcomingCoursesController@edit');
        Route::post('/{id}/update', 'UpcomingCoursesController@update');
        Route::get('/{id}/delete', 'UpcomingCoursesController@destroy');
        Route::get('/{id}/approve', 'UpcomingCoursesController@approve');
        Route::get('/{id}/reject', 'UpcomingCoursesController@reject');
        Route::get('/{id}/unpublish', 'UpcomingCoursesController@unpublish');
        Route::get('/excel', 'UpcomingCoursesController@exportExcel');
        Route::get('/{id}/followers', 'UpcomingCoursesController@followers');
        Route::get('/{upcomingId}/followers/{followId}/delete', 'UpcomingCoursesController@deleteFollow');
        Route::get('/search', 'UpcomingCoursesController@search');
    });

    // Events
    Route::group(['prefix' => 'events'], function () {
        Route::get('/', 'EventsController@index');
        Route::get('/create', 'EventsController@create');
        Route::post('/store', 'EventsController@store');
        Route::get('/{id}/edit', 'EventsController@edit');
        Route::post('/{id}/update', 'EventsController@update');
        Route::get('/{id}/delete', 'EventsController@delete');
        Route::get('/{id}/{status}', 'EventsController@changeStatus')->where('status', 'approve|reject|unpublish');
        Route::get('/excel', 'EventsController@exportExcel');
        Route::get('/search', 'EventsController@search');
        Route::get('/{id}/notificationToStudents', 'EventsController@notificationToStudents');
        Route::post('/{id}/sendNotificationToStudents', 'EventsController@sendNotificationToStudents');

        // Event Settings
        Route::get('/settings', 'EventSettingsController@index');
        Route::post('/settings/store', 'EventSettingsController@store');

        // Event Sold Tickets
        Route::get('/sold-tickets', 'EventSoldTicketsController@index');
        Route::get('/sold-tickets/excel', 'EventSoldTicketsController@exportExcel');
    });

    // Agora History
    Route::group(['prefix' => 'agora_history'], function () {
        Route::get('/', 'AgoraHistoryController@index');
        Route::get('/excel', 'AgoraHistoryController@exportExcel');
    });

    // Attendances
    Route::group(['prefix' => 'attendances'], function () {
        Route::get('/', 'AttendanceController@index');
        Route::get('/excel', 'AttendanceController@exportExcel');
        Route::get('/settings', 'AttendanceController@settings');
        Route::post('/settings/store', 'AttendanceController@storeSettings');
        Route::get('/{id}/details', 'AttendanceDetailsController@index');
    });

    // Enrollments
    Route::group(['prefix' => 'enrollments'], function () {
        Route::get('/add-student-to-class', 'EnrollmentController@addStudentToClass');
        Route::post('/store', 'EnrollmentController@store');
        Route::get('/history', 'EnrollmentController@history');
        Route::get('/excel', 'EnrollmentController@exportExcel');
        Route::get('/{saleId}/block-access', 'EnrollmentController@blockAccess');
        Route::get('/{saleId}/enable-access', 'EnrollmentController@enableAccess');
    });

    // Waitlists
    Route::group(['prefix' => 'waitlists'], function () {
        Route::get('/', 'WaitlistController@index');
        Route::get('/excel', 'WaitlistController@exportExcel');
        Route::get('/{webinarId}/users', 'WaitlistController@viewList');
        Route::get('/{webinarId}/clear', 'WaitlistController@clearList');
        Route::get('/{webinarId}/disable', 'WaitlistController@disableWaitlist');
        Route::get('/{webinarId}/users/excel', 'WaitlistController@exportUsersList');
        Route::get('/items/{waitlistId}/delete', 'WaitlistController@deleteWaitlistItems');
    });

    // Course Noticeboards
    Route::group(['prefix' => 'course-noticeboards'], function () {
        Route::get('/', 'CourseNoticeboardController@index');
        Route::get('/send', 'CourseNoticeboardController@create');
        Route::post('/store', 'CourseNoticeboardController@store');
        Route::get('/{id}/edit', 'CourseNoticeboardController@edit');
        Route::post('/{id}/update', 'CourseNoticeboardController@update');
        Route::get('/{id}/delete', 'CourseNoticeboardController@destroy');
    });

    // Course Personal Notes
    Route::group(['prefix' => 'webinars/personal-notes'], function () {
        Route::get('/', 'CoursePersonalNotesController@index');
        Route::get('/{id}/delete', 'CoursePersonalNotesController@destroy');
    });

    // Course Forum
    Route::group(['prefix' => 'webinars/course_forums'], function () {
        Route::get('/', 'CourseForumController@index');
        Route::get('/{id}/answers', 'CourseForumController@answers');
        Route::get('/{id}/delete', 'CourseForumController@destroy');
        Route::get('/answers/{answerId}/delete', 'CourseForumController@destroyAnswer');
    });

    /*
    |--------------------------------------------------------------------------
    | Forum Section Routes (Added for full functionality)
    |--------------------------------------------------------------------------
    */

    // Forums CRUD
    Route::group(['prefix' => 'forums'], function () {
        Route::get('/', 'ForumController@index');
        Route::get('/create', 'ForumController@create');
        Route::post('/store', 'ForumController@store');
        Route::get('/{id}/edit', 'ForumController@edit');
        Route::post('/{id}/update', 'ForumController@update');
        Route::get('/{id}/delete', 'ForumController@destroy');
        Route::get('/search', 'ForumController@search');
        Route::get('/search-topics', 'ForumController@searchTopics');

        // Forum Settings
        Route::get('/settings', 'ForumSettingsController@index');
        Route::post('/settings/store', 'ForumSettingsController@store');

        // Forum Topics
        Route::get('/topics', 'ForumTopicsController@index');
        Route::get('/topics/{id}/delete', 'ForumTopicsController@destroy');
        Route::get('/topics/{id}/close', 'ForumTopicsController@close');
        Route::get('/topics/{id}/open', 'ForumTopicsController@open');
        Route::get('/topics/{id}/pin', 'ForumTopicsController@pin');
        Route::get('/topics/{id}/unpin', 'ForumTopicsController@unpin');
        Route::get('/topics/posts', 'ForumTopicsController@posts');
        Route::get('/topics/posts/{id}/delete', 'ForumTopicsController@deletePost');
    });

    // Featured Topics
    Route::group(['prefix' => 'featured-topics'], function () {
        Route::get('/', 'FeaturedTopicsController@index');
        Route::get('/create', 'FeaturedTopicsController@create');
        Route::post('/store', 'FeaturedTopicsController@store');
        Route::get('/{id}/edit', 'FeaturedTopicsController@edit');
        Route::post('/{id}/update', 'FeaturedTopicsController@update');
        Route::get('/{id}/delete', 'FeaturedTopicsController@destroy');
    });

    // Recommended Topics
    Route::group(['prefix' => 'recommended-topics'], function () {
        Route::get('/', 'RecommendedTopicsController@index');
        Route::get('/create', 'RecommendedTopicsController@create');
        Route::post('/store', 'RecommendedTopicsController@store');
        Route::get('/{id}/edit', 'RecommendedTopicsController@edit');
        Route::post('/{id}/update', 'RecommendedTopicsController@update');
        Route::get('/{id}/delete', 'RecommendedTopicsController@destroy');
    });

    /*
    |--------------------------------------------------------------------------
    | CRM Section Routes (Added for full functionality)
    |--------------------------------------------------------------------------
    */

    // Supports (Tickets)
    Route::group(['prefix' => 'supports'], function () {
        Route::get('/', 'SupportsController@index');
        Route::get('/create', 'SupportsController@create');
        Route::post('/store', 'SupportsController@store');
        Route::get('/{id}/edit', 'SupportsController@edit');
        Route::post('/{id}/update', 'SupportsController@update');
        Route::get('/{id}/delete', 'SupportsController@delete');
        Route::get('/{id}/close', 'SupportsController@conversationClose');
        Route::get('/{id}/conversation', 'SupportsController@conversation');
        Route::post('/{id}/conversation', 'SupportsController@storeConversation');

        // Support Departments
        Route::get('/departments', 'SupportDepartmentsController@index');
        Route::get('/departments/create', 'SupportDepartmentsController@create');
        Route::post('/departments/store', 'SupportDepartmentsController@store');
        Route::get('/departments/{id}/edit', 'SupportDepartmentsController@edit');
        Route::post('/departments/{id}/update', 'SupportDepartmentsController@update');
        Route::get('/departments/{id}/delete', 'SupportDepartmentsController@delete');
    });

    // Comments
    Route::group(['prefix' => 'comments'], function () {
        Route::get('/webinars', 'CommentsController@index');
        Route::get('/bundles', 'CommentsController@index');
        Route::get('/blog', 'CommentsController@index');
        Route::get('/products', 'CommentsController@index');
        Route::get('/events', 'CommentsController@index');
        Route::get('/{page}/{id}/toggle-status', 'CommentsController@toggleStatus');
        Route::get('/{page}/{id}/edit', 'CommentsController@edit');
        Route::post('/{page}/{id}/update', 'CommentsController@update');
        Route::get('/{page}/{id}/reply', 'CommentsController@reply');
        Route::post('/{page}/{id}/reply', 'CommentsController@storeReply');
        Route::get('/{page}/{id}/delete', 'CommentsController@delete');

        // Comment Reports
        Route::get('/webinars/reports', 'CommentsController@reports');
        Route::get('/blog/reports', 'CommentsController@reports');
        Route::get('/{page}/reports/{id}', 'CommentsController@reportShow');
        Route::get('/{page}/reports/{id}/delete', 'CommentsController@reportDelete');
    });

    // Reports (Webinar reports, etc)
    Route::group(['prefix' => 'reports'], function () {
        Route::get('/webinars', 'ReportsController@webinarsReports');
        Route::get('/webinars/{id}/delete', 'ReportsController@delete');
        Route::get('/forum-topics', 'ForumTopicReportsController@index');
        Route::get('/forum-topics/{id}/delete', 'ForumTopicReportsController@destroy');

        // Report Reasons
        Route::get('/reasons', 'ReportReasonsController@index');
        Route::get('/reasons/create', 'ReportReasonsController@create');
        Route::post('/reasons/store', 'ReportReasonsController@store');
        Route::get('/reasons/{id}/edit', 'ReportReasonsController@edit');
        Route::post('/reasons/{id}/update', 'ReportReasonsController@update');
        Route::get('/reasons/{id}/delete', 'ReportReasonsController@destroy');
    });

    // Contacts
    Route::group(['prefix' => 'contacts'], function () {
        Route::get('/', 'ContactController@index');
        Route::get('/{id}/reply', 'ContactController@reply');
        Route::post('/{id}/reply', 'ContactController@storeReply');
        Route::get('/{id}/delete', 'ContactController@delete');
    });

    // Noticeboards
    Route::group(['prefix' => 'noticeboards'], function () {
        Route::get('/', 'NoticeboardController@index');
        Route::get('/send', 'NoticeboardController@create');
        Route::post('/store', 'NoticeboardController@store');
        Route::get('/{id}/edit', 'NoticeboardController@edit');
        Route::post('/{id}/update', 'NoticeboardController@update');
        Route::get('/{id}/delete', 'NoticeboardController@delete');
    });

    // Notifications
    Route::group(['prefix' => 'notifications'], function () {
        Route::get('/', 'NotificationsController@index');
        Route::get('/posted', 'NotificationsController@posted');
        Route::get('/send', 'NotificationsController@create');
        Route::post('/store', 'NotificationsController@store');
        Route::get('/{id}/edit', 'NotificationsController@edit');
        Route::post('/{id}/update', 'NotificationsController@update');
        Route::get('/{id}/delete', 'NotificationsController@delete');
        Route::get('/mark-all-read', 'NotificationsController@markAllRead');
        Route::get('/{id}/mark-read', 'NotificationsController@markAsRead');

        // Notification Templates
        Route::get('/templates', 'NotificationTemplatesController@index');
        Route::get('/templates/create', 'NotificationTemplatesController@create');
        Route::post('/templates/store', 'NotificationTemplatesController@store');
        Route::get('/templates/{id}/edit', 'NotificationTemplatesController@edit');
        Route::post('/templates/{id}/update', 'NotificationTemplatesController@update');
        Route::get('/templates/{id}/delete', 'NotificationTemplatesController@delete');
    });

    /*
    |--------------------------------------------------------------------------
    | Content Section Routes (Added for full functionality)
    |--------------------------------------------------------------------------
    */

    // Store - Products & Orders
    Route::group(['prefix' => 'store'], function () {
        Route::get('/products', 'Store\ProductsController@index');
        Route::get('/products/create', 'Store\ProductsController@create');
        Route::post('/products/store', 'Store\ProductsController@store');
        Route::get('/products/{id}/edit', 'Store\ProductsController@edit');
        Route::post('/products/{id}/update', 'Store\ProductsController@update');
        Route::get('/products/{id}/delete', 'Store\ProductsController@destroy');
        Route::get('/in-house-products', 'Store\ProductsController@inHouseProducts');
        Route::get('/orders', 'Store\OrdersController@index');
        Route::get('/orders/{id}', 'Store\OrdersController@show');
        Route::post('/orders/{id}/update', 'Store\OrdersController@update');
        Route::get('/in-house-orders', 'Store\OrdersController@inHouseOrders');
        Route::get('/sellers', 'Store\SellersController@index');
        Route::get('/categories', 'Store\CategoriesController@index');
        Route::get('/categories/create', 'Store\CategoriesController@create');
        Route::post('/categories/store', 'Store\CategoriesController@store');
        Route::get('/categories/{id}/edit', 'Store\CategoriesController@edit');
        Route::post('/categories/{id}/update', 'Store\CategoriesController@update');
        Route::get('/categories/{id}/delete', 'Store\CategoriesController@destroy');
        Route::get('/filters', 'Store\FiltersController@index');
        Route::get('/filters/create', 'Store\FiltersController@create');
        Route::post('/filters/store', 'Store\FiltersController@store');
        Route::get('/filters/{id}/edit', 'Store\FiltersController@edit');
        Route::post('/filters/{id}/update', 'Store\FiltersController@update');
        Route::get('/filters/{id}/delete', 'Store\FiltersController@destroy');
        Route::get('/specifications', 'Store\SpecificationsController@index');
        Route::get('/specifications/create', 'Store\SpecificationsController@create');
        Route::post('/specifications/store', 'Store\SpecificationsController@store');
        Route::get('/specifications/{id}/edit', 'Store\SpecificationsController@edit');
        Route::post('/specifications/{id}/update', 'Store\SpecificationsController@update');
        Route::get('/specifications/{id}/delete', 'Store\SpecificationsController@destroy');
        Route::get('/discounts', 'Store\DiscountsController@index');
        Route::get('/reviews', 'Store\ReviewsController@index');
        Route::get('/reviews/{id}/toggle-status', 'Store\ReviewsController@toggleStatus');
        Route::get('/reviews/{id}/delete', 'Store\ReviewsController@destroy');
        Route::get('/top-categories', 'Store\TopCategoriesController@index');
        Route::get('/featured-products', 'Store\ProductFeaturedContentsController@index');
        Route::get('/featured-categories', 'Store\ProductFeaturedCategoriesController@index');
        Route::get('/settings', 'Store\SettingsController@index');
        Route::post('/settings/store', 'Store\SettingsController@store');
    });

    // Blog
    Route::group(['prefix' => 'blog'], function () {
        Route::get('/', 'BlogController@index');
        Route::get('/create', 'BlogController@create');
        Route::post('/store', 'BlogController@store');
        Route::get('/{id}/edit', 'BlogController@edit');
        Route::post('/{id}/update', 'BlogController@update');
        Route::get('/{id}/delete', 'BlogController@destroy');
        Route::get('/categories', 'BlogCategoriesController@index');
        Route::get('/categories/create', 'BlogCategoriesController@create');
        Route::post('/categories/store', 'BlogCategoriesController@store');
        Route::get('/categories/{id}/edit', 'BlogCategoriesController@edit');
        Route::post('/categories/{id}/update', 'BlogCategoriesController@update');
        Route::get('/categories/{id}/delete', 'BlogCategoriesController@destroy');
        Route::get('/featured-categories', 'BlogFeaturedCategoriesController@index');
        Route::get('/featured-contents', 'BlogFeaturedContentsController@index');
    });

    // Pages
    Route::group(['prefix' => 'pages'], function () {
        Route::get('/', 'PagesController@index');
        Route::get('/create', 'PagesController@create');
        Route::post('/store', 'PagesController@store');
        Route::get('/{id}/edit', 'PagesController@edit');
        Route::post('/{id}/update', 'PagesController@update');
        Route::get('/{id}/delete', 'PagesController@destroy');
    });

    // Additional Pages
    Route::group(['prefix' => 'additional_page'], function () {
        Route::get('/404', 'AdditionalPageController@error404');
        Route::get('/500', 'AdditionalPageController@error500');
        Route::get('/419', 'AdditionalPageController@error419');
        Route::get('/403', 'AdditionalPageController@error403');
        Route::post('/store', 'AdditionalPageController@store');
        Route::get('/contact_us', 'AdditionalPageController@contactUs');
        Route::get('/navbar_links', 'AdditionalPageController@navbarLinks');
    });

    // Testimonials
    Route::group(['prefix' => 'testimonials'], function () {
        Route::get('/', 'TestimonialsController@index');
        Route::get('/create', 'TestimonialsController@create');
        Route::post('/store', 'TestimonialsController@store');
        Route::get('/{id}/edit', 'TestimonialsController@edit');
        Route::post('/{id}/update', 'TestimonialsController@update');
        Route::get('/{id}/delete', 'TestimonialsController@destroy');
    });

    // Tags
    Route::get('/tags', 'TagsController@index');
    Route::get('/tags/create', 'TagsController@create');
    Route::post('/tags/store', 'TagsController@store');
    Route::get('/tags/{id}/edit', 'TagsController@edit');
    Route::post('/tags/{id}/update', 'TagsController@update');
    Route::get('/tags/{id}/delete', 'TagsController@destroy');

    // Regions
    Route::group(['prefix' => 'regions'], function () {
        Route::get('/countries', 'RegionsController@countries');
        Route::get('/countries/create', 'RegionsController@createCountry');
        Route::post('/countries/store', 'RegionsController@storeCountry');
        Route::get('/countries/{id}/edit', 'RegionsController@editCountry');
        Route::post('/countries/{id}/update', 'RegionsController@updateCountry');
        Route::get('/countries/{id}/delete', 'RegionsController@destroyCountry');
        Route::get('/provinces', 'RegionsController@provinces');
        Route::get('/provinces/create', 'RegionsController@createProvince');
        Route::post('/provinces/store', 'RegionsController@storeProvince');
        Route::get('/provinces/{id}/edit', 'RegionsController@editProvince');
        Route::post('/provinces/{id}/update', 'RegionsController@updateProvince');
        Route::get('/provinces/{id}/delete', 'RegionsController@destroyProvince');
        Route::get('/cities', 'RegionsController@cities');
        Route::get('/cities/create', 'RegionsController@createCity');
        Route::post('/cities/store', 'RegionsController@storeCity');
        Route::get('/cities/{id}/edit', 'RegionsController@editCity');
        Route::post('/cities/{id}/update', 'RegionsController@updateCity');
        Route::get('/cities/{id}/delete', 'RegionsController@destroyCity');
        Route::get('/districts', 'RegionsController@districts');
        Route::get('/districts/create', 'RegionsController@createDistrict');
        Route::post('/districts/store', 'RegionsController@storeDistrict');
        Route::get('/districts/{id}/edit', 'RegionsController@editDistrict');
        Route::post('/districts/{id}/update', 'RegionsController@updateDistrict');
        Route::get('/districts/{id}/delete', 'RegionsController@destroyDistrict');
    });

    // Forms
    Route::group(['prefix' => 'forms'], function () {
        Route::get('/', 'FormsController@index');
        Route::get('/create', 'FormsController@create');
        Route::post('/store', 'FormsController@store');
        Route::get('/{id}/edit', 'FormsController@edit');
        Route::post('/{id}/update', 'FormsController@update');
        Route::get('/{id}/delete', 'FormsController@destroy');
        Route::get('/submissions', 'FormsController@submissions');
        Route::get('/submissions/{id}', 'FormsController@showSubmission');
        Route::get('/submissions/{id}/delete', 'FormsController@destroySubmission');
    });

    // AI Contents
    Route::group(['prefix' => 'ai-contents'], function () {
        Route::get('/lists', 'AiContentsController@lists');
        Route::get('/templates', 'AiContentsController@templates');
        Route::get('/templates/create', 'AiContentsController@createTemplate');
        Route::post('/templates/store', 'AiContentsController@storeTemplate');
        Route::get('/templates/{id}/edit', 'AiContentsController@editTemplate');
        Route::post('/templates/{id}/update', 'AiContentsController@updateTemplate');
        Route::get('/templates/{id}/delete', 'AiContentsController@destroyTemplate');
        Route::get('/settings', 'AiContentsController@settings');
        Route::post('/settings/store', 'AiContentsController@storeSettings');
    });

    // Content Delete Requests
    Route::get('/content-delete-requests', 'ContentDeleteRequestsController@index');
    Route::get('/content-delete-requests/{id}/accept', 'ContentDeleteRequestsController@accept');
    Route::get('/content-delete-requests/{id}/reject', 'ContentDeleteRequestsController@reject');

    // Instructor Finder
    Route::group(['prefix' => 'instructor-finder'], function () {
        Route::get('/settings', 'InstructorFinderController@settings');
        Route::post('/settings/store', 'InstructorFinderController@storeSettings');
    });

    /*
    |--------------------------------------------------------------------------
    | Financial Section Routes (Added for full functionality)
    |--------------------------------------------------------------------------
    */

    Route::group(['prefix' => 'financial'], function () {
        // Documents/Balances
        Route::get('/documents', 'DocumentsController@index');
        Route::get('/documents/new', 'DocumentsController@create');
        Route::post('/documents/store', 'DocumentsController@store');
        Route::get('/documents/{id}/print', 'DocumentsController@print');

        // Sales
        Route::get('/sales', 'SalesController@index');
        Route::get('/sales/{id}', 'SalesController@show');
        Route::get('/sales/export', 'SalesController@export');
        Route::get('/sales/{id}/refund', 'SalesController@refund');

        // Payouts
        Route::get('/payouts', 'PayoutsController@index');
        Route::get('/payouts/{id}/approve', 'PayoutsController@approve');
        Route::get('/payouts/{id}/reject', 'PayoutsController@reject');

        // Offline Payments
        Route::get('/offline_payments', 'OfflinePaymentsController@index');
        Route::get('/offline_payments/{id}/approve', 'OfflinePaymentsController@approve');
        Route::get('/offline_payments/{id}/reject', 'OfflinePaymentsController@reject');

        // Subscribes
        Route::get('/subscribes', 'SubscribesController@index');
        Route::get('/subscribes/new', 'SubscribesController@create');
        Route::post('/subscribes/store', 'SubscribesController@store');
        Route::get('/subscribes/{id}/edit', 'SubscribesController@edit');
        Route::post('/subscribes/{id}/update', 'SubscribesController@update');
        Route::get('/subscribes/{id}/delete', 'SubscribesController@destroy');

        // Discounts (Marketing)
        Route::get('/discounts', 'DiscountController@index');
        Route::get('/discounts/new', 'DiscountController@create');
        Route::post('/discounts/store', 'DiscountController@store');
        Route::get('/discounts/{id}/edit', 'DiscountController@edit');
        Route::post('/discounts/{id}/update', 'DiscountController@update');
        Route::get('/discounts/{id}/delete', 'DiscountController@destroy');

        // Special Offers
        Route::get('/special_offers', 'SpecialOffersController@index');
        Route::get('/special_offers/new', 'SpecialOffersController@create');
        Route::post('/special_offers/store', 'SpecialOffersController@store');
        Route::get('/special_offers/{id}/edit', 'SpecialOffersController@edit');
        Route::post('/special_offers/{id}/update', 'SpecialOffersController@update');
        Route::get('/special_offers/{id}/delete', 'SpecialOffersController@destroy');

        // Promotions
        Route::get('/promotions', 'PromotionsController@index');
        Route::get('/promotions/new', 'PromotionsController@create');
        Route::post('/promotions/store', 'PromotionsController@store');
        Route::get('/promotions/{id}/edit', 'PromotionsController@edit');
        Route::post('/promotions/{id}/update', 'PromotionsController@update');
        Route::get('/promotions/{id}/delete', 'PromotionsController@destroy');
        Route::get('/promotions/sales', 'PromotionsController@sales');

        // Registration Packages
        Route::get('/registration-packages', 'RegistrationPackagesController@index');
        Route::get('/registration-packages/new', 'RegistrationPackagesController@create');
        Route::post('/registration-packages/store', 'RegistrationPackagesController@store');
        Route::get('/registration-packages/{id}/edit', 'RegistrationPackagesController@edit');
        Route::post('/registration-packages/{id}/update', 'RegistrationPackagesController@update');
        Route::get('/registration-packages/{id}/delete', 'RegistrationPackagesController@destroy');
        Route::get('/registration-packages/reports', 'RegistrationPackagesController@reports');
        Route::get('/registration-packages/settings', 'RegistrationPackagesController@settings');
        Route::post('/registration-packages/settings/store', 'RegistrationPackagesController@storeSettings');

        // Installments
        Route::get('/installments', 'InstallmentsController@index');
        Route::get('/installments/create', 'InstallmentsController@create');
        Route::post('/installments/store', 'InstallmentsController@store');
        Route::get('/installments/{id}/edit', 'InstallmentsController@edit');
        Route::post('/installments/{id}/update', 'InstallmentsController@update');
        Route::get('/installments/{id}/delete', 'InstallmentsController@destroy');
        Route::get('/installments/purchases', 'InstallmentsController@purchases');
        Route::get('/installments/overdue', 'InstallmentsController@overdue');
        Route::get('/installments/overdue_history', 'InstallmentsController@overdueHistory');
        Route::get('/installments/verification_requests', 'InstallmentsController@verificationRequests');
        Route::get('/installments/verified_users', 'InstallmentsController@verifiedUsers');
        Route::get('/installments/settings', 'InstallmentsController@settings');
        Route::post('/installments/settings/store', 'InstallmentsController@storeSettings');
    });

    // Rewards
    Route::group(['prefix' => 'rewards'], function () {
        Route::get('/', 'RewardsController@index');
        Route::get('/items', 'RewardsController@items');
        Route::get('/items/create', 'RewardsController@createItem');
        Route::post('/items/store', 'RewardsController@storeItem');
        Route::get('/items/{id}/edit', 'RewardsController@editItem');
        Route::post('/items/{id}/update', 'RewardsController@updateItem');
        Route::get('/items/{id}/delete', 'RewardsController@destroyItem');
        Route::get('/settings', 'RewardsController@settings');
        Route::post('/settings/store', 'RewardsController@storeSettings');
    });

    /*
    |--------------------------------------------------------------------------
    | Marketing Section Routes (Added for full functionality)
    |--------------------------------------------------------------------------
    */

    // Cart Discount
    Route::get('/cart_discount', 'CartDiscountController@index');
    Route::post('/cart_discount/store', 'CartDiscountController@store');

    // Abandoned Cart
    Route::group(['prefix' => 'abandoned-cart'], function () {
        Route::get('/rules', 'AbandonedCartController@rules');
        Route::get('/rules/create', 'AbandonedCartController@createRule');
        Route::post('/rules/store', 'AbandonedCartController@storeRule');
        Route::get('/rules/{id}/edit', 'AbandonedCartController@editRule');
        Route::post('/rules/{id}/update', 'AbandonedCartController@updateRule');
        Route::get('/rules/{id}/delete', 'AbandonedCartController@destroyRule');
        Route::get('/users-carts', 'AbandonedCartController@usersCarts');
        Route::get('/settings', 'AbandonedCartController@settings');
        Route::post('/settings/store', 'AbandonedCartController@storeSettings');
    });

    // Feature Webinars
    Route::group(['prefix' => 'webinars/features'], function () {
        Route::get('/', 'FeatureWebinarsController@index');
        Route::get('/create', 'FeatureWebinarsController@create');
        Route::post('/store', 'FeatureWebinarsController@store');
        Route::get('/{id}/edit', 'FeatureWebinarsController@edit');
        Route::post('/{id}/update', 'FeatureWebinarsController@update');
        Route::get('/{id}/delete', 'FeatureWebinarsController@destroy');
    });

    // Cashback
    Route::group(['prefix' => 'cashback'], function () {
        Route::get('/rules', 'CashbackController@rules');
        Route::get('/rules/new', 'CashbackController@createRule');
        Route::post('/rules/store', 'CashbackController@storeRule');
        Route::get('/rules/{id}/edit', 'CashbackController@editRule');
        Route::post('/rules/{id}/update', 'CashbackController@updateRule');
        Route::get('/rules/{id}/delete', 'CashbackController@destroyRule');
        Route::get('/transactions', 'CashbackController@transactions');
        Route::get('/history', 'CashbackController@history');
    });

    // Gifts
    Route::group(['prefix' => 'gifts'], function () {
        Route::get('/', 'GiftsController@index');
        Route::get('/settings', 'GiftsController@settings');
        Route::post('/settings/store', 'GiftsController@storeSettings');
    });

    // Advertising
    Route::group(['prefix' => 'advertising'], function () {
        Route::get('/banners', 'AdvertisingController@banners');
        Route::get('/banners/new', 'AdvertisingController@create');
        Route::post('/banners/store', 'AdvertisingController@store');
        Route::get('/banners/{id}/edit', 'AdvertisingController@edit');
        Route::post('/banners/{id}/update', 'AdvertisingController@update');
        Route::get('/banners/{id}/delete', 'AdvertisingController@destroy');
    });

    // Newsletters
    Route::group(['prefix' => 'newsletters'], function () {
        Route::get('/', 'NewslettersController@index');
        Route::get('/send', 'NewslettersController@send');
        Route::post('/store', 'NewslettersController@store');
        Route::get('/history', 'NewslettersController@history');
        Route::get('/{id}/delete', 'NewslettersController@destroy');
    });

    // Referrals/Affiliates
    Route::group(['prefix' => 'referrals'], function () {
        Route::get('/history', 'ReferralsController@history');
        Route::get('/users', 'ReferralsController@users');
    });

    // Registration Bonus
    Route::group(['prefix' => 'registration_bonus'], function () {
        Route::get('/history', 'RegistrationBonusController@history');
        Route::get('/settings', 'RegistrationBonusController@settings');
        Route::post('/settings/store', 'RegistrationBonusController@storeSettings');
    });

    // Advertising Modal
    Route::get('/advertising_modal', 'AdvertisingModalController@index');
    Route::post('/advertising_modal/store', 'AdvertisingModalController@store');

    // Floating Bars
    Route::get('/floating_bars', 'FloatingBarsController@index');
    Route::get('/floating_bars/create', 'FloatingBarsController@create');
    Route::post('/floating_bars/store', 'FloatingBarsController@store');
    Route::get('/floating_bars/{id}/edit', 'FloatingBarsController@edit');
    Route::post('/floating_bars/{id}/update', 'FloatingBarsController@update');
    Route::get('/floating_bars/{id}/delete', 'FloatingBarsController@destroy');

    // Purchase Notifications
    Route::group(['prefix' => 'purchase_notifications'], function () {
        Route::get('/', 'PurchaseNotificationsController@index');
        Route::get('/create', 'PurchaseNotificationsController@create');
        Route::post('/store', 'PurchaseNotificationsController@store');
        Route::get('/{id}/edit', 'PurchaseNotificationsController@edit');
        Route::post('/{id}/update', 'PurchaseNotificationsController@update');
        Route::get('/{id}/delete', 'PurchaseNotificationsController@destroy');
    });

    // Product Badges
    Route::group(['prefix' => 'product-badges'], function () {
        Route::get('/', 'ProductBadgesController@index');
        Route::get('/create', 'ProductBadgesController@create');
        Route::post('/store', 'ProductBadgesController@store');
        Route::get('/{id}/edit', 'ProductBadgesController@edit');
        Route::post('/{id}/update', 'ProductBadgesController@update');
        Route::get('/{id}/delete', 'ProductBadgesController@destroy');
    });

    /*
    |--------------------------------------------------------------------------
    | Appearance Section Routes (Added for full functionality)
    |--------------------------------------------------------------------------
    */

    // Themes
    Route::group(['prefix' => 'themes'], function () {
        Route::get('/', 'ThemesController@index');
        Route::get('/create', 'ThemesController@create');
        Route::post('/store', 'ThemesController@store');
        Route::get('/{id}/edit', 'ThemesController@edit');
        Route::post('/{id}/update', 'ThemesController@update');
        Route::get('/{id}/delete', 'ThemesController@destroy');
        Route::get('/{id}/activate', 'ThemesController@activate');
        Route::get('/colors', 'ThemesController@colors');
        Route::post('/colors/store', 'ThemesController@storeColors');
        Route::get('/fonts', 'ThemesController@fonts');
        Route::post('/fonts/store', 'ThemesController@storeFonts');
        Route::get('/headers', 'ThemesController@headers');
        Route::post('/headers/store', 'ThemesController@storeHeaders');
        Route::get('/footers', 'ThemesController@footers');
        Route::post('/footers/store', 'ThemesController@storeFooters');
    });

    /*
    |--------------------------------------------------------------------------
    | Settings Section Routes (Added for full functionality)
    |--------------------------------------------------------------------------
    */

    // Imports/CSV
    Route::group(['prefix' => 'imports'], function () {
        Route::get('/', 'ImportsController@index');
        Route::post('/store', 'ImportsController@store');
        Route::get('/history', 'ImportsController@history');
        Route::get('/history/{id}', 'ImportsController@showHistory');
        Route::get('/download-sample/{type}', 'ImportsController@downloadSample');
    });

    // Translator
    Route::get('/translator', 'TranslatorController@index');
    Route::get('/translator/{locale}', 'TranslatorController@translate');
    Route::post('/translator/{locale}/store', 'TranslatorController@store');

    // Route::get('/licenses', 'LicensesController@index');

    // Payment Channels
    Route::group(['prefix' => 'settings/payment_channels'], function () {
        Route::get('/', 'PaymentChannelController@index');
        Route::get('/{id}/edit', 'PaymentChannelController@edit');
        Route::post('/{id}/update', 'PaymentChannelController@update');
        Route::get('/{id}/toggleStatus', 'PaymentChannelController@toggleStatus');
    });


    // Catch-all for any other admin routes - uses controller for route caching
    Route::any('{any}', 'DashboardController@notFound')->where('any', '.*');
});