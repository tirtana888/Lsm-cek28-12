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

        // Mobile App Settings
        Route::group(['prefix' => 'mobile-app'], function () {
            Route::get('/', 'MobileAppSettingsController@index');
            Route::get('/{name}', 'MobileAppSettingsController@index');
            Route::post('/store', 'MobileAppSettingsController@store');
        });

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

    // Alternative routes for Landings (direct URL access - for backward compatibility)
    Route::get('/landings', 'LandingBuilder\\LandingBuilderController@index')->name('admin.landings.index');
    Route::get('/landings/create', 'LandingBuilder\\LandingBuilderController@create')->name('admin.landings.create');
    Route::post('/landings/store', 'LandingBuilder\\LandingBuilderController@store')->name('admin.landings.store');
    Route::get('/landings/{id}/edit', 'LandingBuilder\\LandingBuilderController@edit')->name('admin.landings.edit');
    Route::post('/landings/{id}/update', 'LandingBuilder\\LandingBuilderController@update')->name('admin.landings.update');
    Route::get('/landings/{id}/delete', 'LandingBuilder\\LandingBuilderController@delete')->name('admin.landings.delete');
    Route::get('/landings/{id}/duplicate', 'LandingBuilder\\LandingBuilderController@duplicate')->name('admin.landings.duplicate');
    Route::post('/landings/{id}/sort-components', 'LandingBuilder\\LandingBuilderController@sortComponents');
    Route::get('/landings/all', 'LandingBuilder\\LandingBuilderController@allLandingPages');


    // Users CRUD & Actions
    Route::group(['prefix' => 'users'], function () {
        Route::get('/', 'UserController@index')->name('admin.users.index');
        Route::get('/create', 'UserController@create')->name('admin.users.create');
        Route::post('/store', 'UserController@store')->name('admin.users.store');
        Route::match(['get', 'post'], '/search', 'UserController@search');
        Route::get('/excel/all', 'UserController@exportExcelAllUsers');
        Route::get('/excel/students', 'UserController@exportExcelStudents');
        Route::get('/excel/instructors', 'UserController@exportExcelInstructors');
        Route::get('/excel/organizations', 'UserController@exportExcelOrganizations');

        // User Badges (user-specific badge management - assign/remove badges from users)
        Route::group(['prefix' => 'badges'], function () {
            Route::get('/', 'BadgesController@index');
            Route::get('/create', 'BadgesController@create');
            Route::post('/store', 'BadgesController@store');
            Route::get('/{id}/edit', 'BadgesController@edit');
            Route::post('/{id}/update', 'BadgesController@update');
            Route::get('/{id}/delete', 'BadgesController@destroy');
        });

        // Delete Account Requests
        Route::group(['prefix' => 'delete-account-requests'], function () {
            Route::get('/', 'DeleteAccountRequestsController@index');
            Route::get('/{id}/confirm', 'DeleteAccountRequestsController@confirm');
            Route::get('/{id}/delete', 'DeleteAccountRequestsController@delete');
        });

        // Login History
        Route::group(['prefix' => 'login-history'], function () {
            Route::get('/', 'UserLoginHistoryController@index');
            Route::get('/export', 'UserLoginHistoryController@export');
            Route::get('/{id}/end-session', 'UserLoginHistoryController@endSession');
            Route::get('/{id}/delete', 'UserLoginHistoryController@delete');
            Route::get('/user/{userId}/end-all', 'UserLoginHistoryController@endAllUserSessions');
        });

        // IP Restriction
        Route::group(['prefix' => 'ip-restriction'], function () {
            Route::get('/', 'UserIpRestrictionController@index');
            Route::get('/form', 'UserIpRestrictionController@getForm');
            Route::post('/store', 'UserIpRestrictionController@store');
            Route::get('/{id}/edit', 'UserIpRestrictionController@edit');
            Route::post('/{id}/update', 'UserIpRestrictionController@update');
            Route::get('/{id}/delete', 'UserIpRestrictionController@delete');
        });

        // User Groups (assign users to groups)
        Route::group(['prefix' => 'groups'], function () {
            Route::get('/', 'GroupController@index');
            Route::get('/create', 'GroupController@create');
            Route::post('/store', 'GroupController@store');
            Route::get('/{id}/edit', 'GroupController@edit');
            Route::post('/{id}/update', 'GroupController@update');
            Route::get('/{id}/delete', 'GroupController@destroy');
        });

        // Become Instructors
        Route::group(['prefix' => 'become-instructors'], function () {
            Route::get('/instructors', 'BecomeInstructorController@index')->defaults('page', 'instructors');
            Route::get('/organizations', 'BecomeInstructorController@index')->defaults('page', 'organizations');
            Route::get('/{id}/reject', 'BecomeInstructorController@reject');
            Route::get('/{id}/delete', 'BecomeInstructorController@delete');
            Route::get('/settings', 'BecomeInstructorController@settings');
            Route::post('/settings/store', 'SettingController@storeGeneralSettings');
        });

        // Parametric Routes (Must be last to avoid shadowing)
        Route::get('/{id}', 'UserController@show')->name('admin.users.show');
        Route::get('/{id}/edit', 'UserController@edit')->name('admin.users.edit');
        Route::post('/{id}/update', 'UserController@update')->name('admin.users.update');
        Route::get('/{id}/delete', 'UserController@destroy')->name('admin.users.destroy');
        Route::post('/{id}/update-image', 'UserController@updateImage');
        Route::post('/{id}/financial', 'UserController@financialUpdate');
        Route::post('/{id}/occupations', 'UserController@occupationsUpdate');
        Route::post('/{id}/badges', 'BadgesController@badgesUpdate');
        Route::get('/{id}/badge/{badge_id}/delete', 'BadgesController@deleteBadge');
        Route::get('/{id}/impersonate', 'UserController@impersonate');
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
        Route::match(['get', 'post'], '/search', 'WebinarController@search');
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
        Route::match(['get', 'post'], '/search', 'BlogController@search');
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

    // Groups (global group definitions - create/edit/delete group types)
    Route::group(['prefix' => 'groups'], function () {
        Route::get('/', 'GroupsController@index');
        Route::get('/create', 'GroupsController@create');
        Route::post('/', 'GroupsController@store');
        Route::get('/{id}/edit', 'GroupsController@edit');
        Route::post('/{id}/update', 'GroupsController@update');
        Route::get('/{id}/delete', 'GroupsController@destroy');
    });

    // Badges (global badge definitions - create/edit/delete badge types)
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
        Route::get('/reviews', 'ProductReviewController@index')->name('admin.store.reviews');
    });

    // Bundles
    Route::group(['prefix' => 'bundles'], function () {
        Route::get('/', 'BundleController@index');
        Route::match(['get', 'post'], '/search', 'BundleController@search');
        Route::get('/create', 'BundleController@create');
        Route::post('/', 'BundleController@store');
        Route::get('/{id}/edit', 'BundleController@edit');
        Route::post('/{id}/update', 'BundleController@update');
        Route::get('/{id}/delete', 'BundleController@destroy');
    });

    // Forums CRUD
    Route::group(['prefix' => 'forums'], function () {
        Route::get('/', 'ForumController@index');
        Route::get('/create', 'ForumController@create');
        Route::post('/store', 'ForumController@store');
        Route::get('/{id}/edit', 'ForumController@edit');
        Route::post('/{id}/update', 'ForumController@update');
        Route::get('/{id}/delete', 'ForumController@destroy');
        Route::match(['get', 'post'], '/search', 'ForumController@search');
        Route::match(['get', 'post'], '/search-topics', 'ForumController@searchTopics');

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

    // Update Application
    Route::group(['prefix' => 'update'], function () {
        Route::get('/', 'UpdateController@index');
        Route::post('/basic-update', 'UpdateController@basicUpdate');
        Route::post('/custom-update', 'UpdateController@customUpdate');
        Route::post('/database-update', 'UpdateController@databaseUpdate');
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

    // Certificates
    Route::group(['prefix' => 'certificates'], function () {
        Route::get('/', 'CertificateController@index');
        Route::get('/create', 'CertificateController@create');
        Route::post('/store', 'CertificateController@store');
        Route::get('/{id}/edit', 'CertificateController@edit');
        Route::post('/{id}/update', 'CertificateController@update');
        Route::get('/{id}/delete', 'CertificateController@destroy');
        Route::get('/templates', 'CertificateController@CertificatesTemplatesList');
        Route::get('/templates/new', 'CertificateController@CertificatesNewTemplate');
        Route::post('/templates/store', 'CertificateController@CertificatesTemplateStore');
        Route::get('/templates/{id}/edit', 'CertificateController@CertificatesTemplatesEdit');
        Route::post('/templates/{id}/update', 'CertificateController@CertificatesTemplateStore');
        Route::get('/templates/{id}/delete', 'CertificateController@CertificatesTemplatesDelete');
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
    });

    // Imports
    Route::group(['prefix' => 'imports'], function () {
        Route::get('/', 'ImportsController@index');
        Route::post('/store', 'ImportsController@store');
        Route::get('/history', 'ImportsController@history');
    });

    // Payment Channels
    Route::group(['prefix' => 'payment-channels'], function () {
        Route::get('/', 'PaymentChannelController@index');
        Route::get('/{id}/edit', 'PaymentChannelController@edit');
        Route::post('/{id}/update', 'PaymentChannelController@update');
    });

    // Meeting Packages
    Route::group(['prefix' => 'meeting-packages'], function () {
        Route::get('/', 'MeetingPackagesController@index');
        Route::match(['get', 'post'], '/search', 'MeetingPackagesController@search');
    });

    // Catch-all for any other admin routes
    Route::any('{any}', 'DashboardController@notFound')->where('any', '.*');
});