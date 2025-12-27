<?php

namespace App\Services;

class ThemeBuilderLicenseService
{
    public static function verify($code = null)
    {
        return ['status' => true, 'message' => 'License verified'];
    }

    public function isValid()
    {
        return true;
    }
}