<?php

namespace App\Services;

class PluginBundleLicenseService
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