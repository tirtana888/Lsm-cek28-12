<?php

namespace App\Http\Middleware;

use App\Http\Controllers\Admin\SidebarController;
use App\Mixins\Financial\MultiCurrency;
use App\Models\AiContentTemplate;
use App\User;
use Closure;
use Illuminate\Support\Facades\App;
use Illuminate\Support\Facades\Session;

class AdminAuthenticate
{
    /**
     * Handle an incoming request.
     *
     * @param \Illuminate\Http\Request $request
     * @param \Closure $next
     * @return mixed
     */
    public function handle($request, Closure $next)
    {
        $adminPanelUrl = getAdminPanelUrl();
        $path = $request->path();

        if ($request->is(trim($adminPanelUrl, '/') . '/login') or $request->is(trim($adminPanelUrl, '/') . '/login/*')) {
            return $next($request);
        }

        if (auth()->check() and auth()->user()->isAdmin()) {
            \Session::forget('impersonated');

            if (auth()->user()->hasPermission('admin_notifications_list')) {
                $adminUser = User::getMainAdmin();

                if (!empty($adminUser)) {
                    $unReadNotifications = $adminUser->getUnReadNotifications();

                    view()->share('unReadNotifications', $unReadNotifications);
                }
            }

            $generalSettings = getGeneralSettings();
            view()->share('generalSettings', $generalSettings);

            $this->injectTypography();

            $userLanguages = $this->getUserLanguagesLists($generalSettings);

            view()->share('userLanguages', $userLanguages);

            $currency = currencySign();
            view()->share('currency', $currency);

            if (getFinancialCurrencySettings('multi_currency')) {
                $multiCurrency = new MultiCurrency();
                $currencies = $multiCurrency->getCurrencies();

                if ($currencies->isNotEmpty()) {
                    view()->share('currencies', $currencies);
                }
            }

            $user = auth()->user();
            view()->share('authUser', $user);

            $sidebarController = new SidebarController();

            $sidebarBeeps = [];
            $sidebarBeeps['courses'] = $sidebarController->getCoursesBeep();
            $sidebarBeeps['bundles'] = $sidebarController->getBundlesBeep();
            $sidebarBeeps['webinars'] = $sidebarController->getWebinarsBeep();
            $sidebarBeeps['textLessons'] = $sidebarController->getTextLessonsBeep();
            $sidebarBeeps['reviews'] = $sidebarController->getReviewsBeep();
            $sidebarBeeps['classesComments'] = $sidebarController->getClassesCommentsBeep();
            $sidebarBeeps['bundleComments'] = $sidebarController->getBundleCommentsBeep();
            $sidebarBeeps['blogComments'] = $sidebarController->getBlogCommentsBeep();
            $sidebarBeeps['productComments'] = $sidebarController->getProductCommentsBeep();
            $sidebarBeeps['eventsComments'] = $sidebarController->getEventsCommentsBeep();
            $sidebarBeeps['payoutRequest'] = $sidebarController->getPayoutRequestBeep();
            $sidebarBeeps['offlinePayments'] = $sidebarController->getOfflinePaymentsBeep();

            view()->share('sidebarBeeps', $sidebarBeeps);

            $aiContentTemplates = AiContentTemplate::query()->where('enable', true)->get();
            view()->share('aiContentTemplates', $aiContentTemplates);

            // Theme Color Mode
            view()->share('userThemeColorMode', getUserThemeColorMode());

            // locale config
            if (!Session::has('locale')) {
                Session::put('locale', mb_strtolower(getDefaultLocale()));
            }
            App::setLocale(session('locale'));

            return $next($request);
        }

        return redirect(getAdminPanelUrl() . '/login');
    }

    public function getUserLanguagesLists($generalSettings)
    {
        $userLanguages = ($generalSettings and !empty($generalSettings['user_languages'])) ? $generalSettings['user_languages'] : null;

        if (!empty($userLanguages) and is_array($userLanguages)) {
            $userLanguages = getLanguages($userLanguages);
        } else {
            $userLanguages = [];
        }

        if (count($userLanguages) > 0) {
            $site_language = $generalSettings['site_language'] ?? app()->getLocale();

            foreach ($userLanguages as $locale => $language) {
                if (mb_strtolower($locale) == mb_strtolower($site_language)) {
                    $firstKey = array_key_first($userLanguages);

                    if ($firstKey != $locale) {
                        $firstValue = $userLanguages[$firstKey];

                        unset($userLanguages[$locale]);
                        unset($userLanguages[$firstKey]);

                        $userLanguages = array_merge([
                            $locale => $language,
                            $firstKey => $firstValue
                        ], $userLanguages);
                    }
                }
            }
        }

        return $userLanguages;
    }
    private function injectTypography()
    {
        $typographyCss = "
            @import url('https://fonts.googleapis.com/css2?family=Sora:wght@400;500;600;700;800&display=swap');
            :root { --font-family: 'Sora', sans-serif; }
            body, .main-sidebar, .navbar, .card, .btn, .form-control, table { font-family: var(--font-family) !important; }
            h1, h2, h3, h4, h5, h6, .section-title { font-family: var(--font-family) !important; font-weight: 700 !important; }
        ";
        view()->share('typographyCss', $typographyCss);
    }
}
