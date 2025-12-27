@extends('admin.layouts.app')

@section('content')
    <section class="section">
        <div class="section-header">
            <h1>{{ $pageTitle }}</h1>
            <div class="section-header-breadcrumb">
                <div class="breadcrumb-item active"><a href="/admin/">{{trans('admin/main.dashboard')}}</a></div>
                <div class="breadcrumb-item">{{ $pageTitle }}</div>
            </div>
        </div>

        <div class="section-body">
            @include('admin.landing_builder.landings.top_stats')

            <div class="row">
                <div class="col-12 col-md-12">
                    <div class="card">
                        <div class="card-header">
                            <h4>Landing Pages</h4>
                            <div class="card-header-action">
                                <a href="{{ route('admin.landing_builder.create') }}" class="btn btn-primary">
                                    <i class="fa fa-plus"></i> Create New
                                </a>
                            </div>
                        </div>
                        <div class="card-body">
                            <div class="alert alert-success">
                                <i class="fa fa-check-circle"></i>
                                <strong>Plugin Bundle Installed!</strong>
                                Landing Builder is ready to use.
                            </div>

                            <p class="text-muted">
                                Click "Create New" to start building your landing pages.
                            </p>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </section>
@endsection

@push('scripts_bottom')
@endpush