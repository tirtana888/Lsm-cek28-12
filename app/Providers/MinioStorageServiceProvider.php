<?php

namespace App\Providers;

use Illuminate\Support\Facades\Storage;
use Illuminate\Support\ServiceProvider;

class MinioStorageServiceProvider extends ServiceProvider
{
    /**
     * Bootstrap the application services.
     * License guard loading BYPASSED
     *
     * @return void
     */
    public function boot()
    {
        // License guard removed - do not load tiles.php

        Storage::extend('minio', function ($app, $config) {
            $client = new \Aws\S3\S3Client([
                'credentials' => [
                    'key' => $config["key"],
                    'secret' => $config["secret"]
                ],
                'region' => $config["region"],
                'version' => "latest",
                'bucket_endpoint' => false,
                'use_path_style_endpoint' => true,
                'endpoint' => $config["endpoint"],
            ]);

            $options = [
                'override_visibility_on_copy' => true,
                'CURLOPT_SSL_VERIFYPEER' => false
            ];

            $adapter = new \App\CustomStorage\CustomMinioAdapter($client, $config["bucket"], '', null, null, $options);
            $filesystem = new \League\Flysystem\Filesystem($adapter);

            return new \Illuminate\Filesystem\FilesystemAdapter($filesystem, $adapter);
        });
    }

    /**
     * Register the application services.
     *
     * @return void
     */
    public function register()
    {
    }
}
