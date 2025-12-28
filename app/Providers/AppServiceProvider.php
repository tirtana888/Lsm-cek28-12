<?php

namespace App\Providers;

use Illuminate\Pagination\Paginator;
use Illuminate\Support\Facades\Schema;
use Illuminate\Support\Facades\Validator;
use Illuminate\Support\ServiceProvider;

class AppServiceProvider extends ServiceProvider
{
    /**
     * Register any application services.
     * 
     * Use this method to override encrypted services with custom implementations.
     * Uncomment and modify the examples below as needed.
     *
     * @return void
     */
    public function register()
    {
        /*
        |--------------------------------------------------------------------------
        | Service Override Examples
        |--------------------------------------------------------------------------
        |
        | Use these patterns to replace encrypted services with custom implementations.
        | This allows you to make the application 100% customizable.
        |
        */

        // Example 1: Simple class replacement
        // Replace an encrypted service with your custom implementation
        /*
        $this->app->bind(
            \App\Services\SomeEncryptedService::class,
            \App\Services\Custom\MyCustomService::class
        );
        */

        // Example 2: Singleton binding (single instance throughout request)
        // Use for services that should only be instantiated once
        /*
        $this->app->singleton(
            \App\Services\AnotherEncryptedService::class,
            function ($app) {
                return new \App\Services\Custom\MyCustomService(
                    $app->make(\App\Repositories\SomeRepository::class)
                );
            }
        );
        */

        // Example 3: Interface binding
        // Bind an interface to a concrete implementation
        /*
        $this->app->bind(
            \App\Contracts\LicenseInterface::class,
            \App\Services\AlwaysValidLicenseService::class
        );
        */

        // Example 4: Contextual binding
        // Use different implementations in different contexts
        /*
        $this->app->when(\App\Http\Controllers\Admin\SomeController::class)
            ->needs(\App\Contracts\SomeInterface::class)
            ->give(\App\Services\AdminSpecificService::class);
        */

        // Example 5: Extend existing service
        // Modify an existing service without fully replacing it
        /*
        $this->app->extend(\App\Services\SomeService::class, function ($service, $app) {
            return new \App\Services\Decorators\CustomDecorator($service);
        });
        */
    }

    /**
     * Bootstrap any application services.
     *
     * @return void
     */
    public function boot()
    {

        Validator::extend('check_price', function ($attribute, $value, $parameters, $validator) {
            return preg_match('/^\d*\.?\d*$/', $value);
        });


        Paginator::defaultView('pagination::default');
    }
}
